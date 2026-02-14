from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from app.models.models import SiteAnalytics
from .serializers import TrackPageViewSerializer
from datetime import datetime, timedelta


@api_view(['POST'])
def track_page_view(request):
    """Record a page view event from the frontend."""
    serializer = TrackPageViewSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # Get IP address from request
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR', '')

    SiteAnalytics.objects.create(
        session_id=data['session_id'],
        visitor_id=data['visitor_id'],
        page_path=data['page_path'],
        page_title=data.get('page_title', ''),
        referrer=data.get('referrer', ''),
        user_agent=data.get('user_agent', ''),
        device_type=data.get('device_type', 'desktop'),
        ip_address=ip_address,
    )
    return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def analytics_summary(request):
    """
    Returns analytics summary for a date range.
    Query params: start (YYYY-MM-DD), end (YYYY-MM-DD)
    Returns: daily breakdown of unique_visitors, sessions, bounce_rate
    """
    start_str = request.query_params.get('start')
    end_str = request.query_params.get('end')

    if not start_str or not end_str:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
    else:
        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

    # Include the end date fully (until end of day)
    end_datetime = datetime.combine(end_date, datetime.max.time())
    start_datetime = datetime.combine(start_date, datetime.min.time())

    # Get all page views in range
    qs = SiteAnalytics.objects.filter(
        created_at__gte=start_datetime,
        created_at__lte=end_datetime,
    )

    # Daily breakdown using raw SQL for complex aggregation
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                DATE(created_at) as day,
                COUNT(DISTINCT visitor_id) as unique_visitors,
                COUNT(DISTINCT session_id) as sessions,
                COUNT(*) as page_views
            FROM site_analytics
            WHERE created_at >= %s AND created_at <= %s
            GROUP BY DATE(created_at)
            ORDER BY day
        """, [start_datetime, end_datetime])
        daily_rows = cursor.fetchall()

    # Calculate bounce rate per day (sessions with only 1 page view)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                DATE(created_at) as day,
                COUNT(*) as total_sessions,
                SUM(CASE WHEN page_count = 1 THEN 1 ELSE 0 END) as bounced_sessions
            FROM (
                SELECT session_id, DATE(created_at) as created_at, COUNT(*) as page_count
                FROM site_analytics
                WHERE created_at >= %s AND created_at <= %s
                GROUP BY session_id, DATE(created_at)
            ) sub
            GROUP BY DATE(created_at)
            ORDER BY day
        """, [start_datetime, end_datetime])
        bounce_rows = cursor.fetchall()

    bounce_map = {}
    for row in bounce_rows:
        day_str = row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])
        total = row[1]
        bounced = row[2]
        bounce_map[day_str] = round((bounced / total * 100) if total > 0 else 0, 1)

    # Build daily data array
    daily_data = []
    for row in daily_rows:
        day_str = row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])
        daily_data.append({
            'date': day_str,
            'visitors': row[1],
            'sessions': row[2],
            'pageViews': row[3],
            'bounceRate': bounce_map.get(day_str, 0),
        })

    # Fill in missing dates with zeros
    all_dates = {}
    current = start_date
    while current <= end_date:
        all_dates[current.strftime('%Y-%m-%d')] = {
            'date': current.strftime('%Y-%m-%d'),
            'visitors': 0,
            'sessions': 0,
            'pageViews': 0,
            'bounceRate': 0,
        }
        current += timedelta(days=1)

    for item in daily_data:
        all_dates[item['date']] = item

    sorted_data = sorted(all_dates.values(), key=lambda x: x['date'])

    # Totals
    total_visitors = qs.values('visitor_id').distinct().count()
    total_sessions = qs.values('session_id').distinct().count()
    total_page_views = qs.count()

    # Overall bounce rate
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                COUNT(*) as total_sessions,
                SUM(CASE WHEN page_count = 1 THEN 1 ELSE 0 END) as bounced
            FROM (
                SELECT session_id, COUNT(*) as page_count
                FROM site_analytics
                WHERE created_at >= %s AND created_at <= %s
                GROUP BY session_id
            ) sub
        """, [start_datetime, end_datetime])
        row = cursor.fetchone()
        overall_bounce = round((row[1] / row[0] * 100) if row[0] > 0 else 0, 1)

    return Response({
        'totals': {
            'visitors': total_visitors,
            'sessions': total_sessions,
            'pageViews': total_page_views,
            'bounceRate': overall_bounce,
        },
        'daily': sorted_data,
    })


@api_view(['GET'])
def page_stats(request):
    """
    Returns top pages with visit counts, percentages, and device breakdown.
    Query params: start (YYYY-MM-DD), end (YYYY-MM-DD), limit (int, default 10)
    """
    start_str = request.query_params.get('start')
    end_str = request.query_params.get('end')
    limit = int(request.query_params.get('limit', 10))

    if not start_str or not end_str:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
    else:
        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)

    end_datetime = datetime.combine(end_date, datetime.max.time())
    start_datetime = datetime.combine(start_date, datetime.min.time())

    # Top pages with device breakdown
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                page_path,
                COUNT(*) as total_views,
                COUNT(DISTINCT visitor_id) as unique_visitors,
                SUM(CASE WHEN device_type = 'desktop' THEN 1 ELSE 0 END) as desktop_views,
                SUM(CASE WHEN device_type = 'mobile' THEN 1 ELSE 0 END) as mobile_views,
                SUM(CASE WHEN device_type = 'tablet' THEN 1 ELSE 0 END) as tablet_views
            FROM site_analytics
            WHERE created_at >= %s AND created_at <= %s
            GROUP BY page_path
            ORDER BY total_views DESC
            LIMIT %s
        """, [start_datetime, end_datetime, limit])
        rows = cursor.fetchall()

    # Total views for percentage calculation
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM site_analytics
            WHERE created_at >= %s AND created_at <= %s
        """, [start_datetime, end_datetime])
        total = cursor.fetchone()[0] or 1

    pages = []
    for row in rows:
        pages.append({
            'page_path': row[0],
            'total_views': row[1],
            'unique_visitors': row[2],
            'percentage': round(row[1] / total * 100, 1),
            'desktop': row[3],
            'mobile': row[4],
            'tablet': row[5],
            'desktop_pct': round(row[3] / row[1] * 100, 1) if row[1] > 0 else 0,
            'mobile_pct': round(row[4] / row[1] * 100, 1) if row[1] > 0 else 0,
            'tablet_pct': round(row[5] / row[1] * 100, 1) if row[1] > 0 else 0,
        })

    return Response({
        'total_views': total,
        'pages': pages,
    })


@api_view(['GET'])
def recent_updates(request):
    """Return recently updated content from various tables."""
    limit = int(request.query_params.get('limit', 10))

    with connection.cursor() as cur:
        # UNION query across tables that have timestamps
        cur.execute("""
            (
                SELECT 'news' AS type,
                       n.id,
                       COALESCE(nt.label, 'Мэдээ #' || n.id) AS title,
                       n.date AS updated_at
                FROM news n
                LEFT JOIN news_title_translations nt
                    ON n.id = nt.news AND nt.language = 2
                WHERE n.date IS NOT NULL
            )
            UNION ALL
            (
                SELECT 'job' AS type,
                       j.id,
                       COALESCE(jt.title, 'Ажлын зар #' || j.id) AS title,
                       j.date AS updated_at
                FROM jobs j
                LEFT JOIN job_translations jt
                    ON j.id = jt.job AND jt.language = 2
                WHERE j.date IS NOT NULL
            )
            UNION ALL
            (
                SELECT 'service' AS type,
                       s.id,
                       COALESCE(st.title, 'Үйлчилгээ #' || s.id) AS title,
                       COALESCE(s.updated_at, s.created_at) AS updated_at
                FROM "Services" s
                LEFT JOIN "Services_translations" st
                    ON s.id = st.service AND st.language = 2
                WHERE s.updated_at IS NOT NULL OR s.created_at IS NOT NULL
            )
            UNION ALL
            (
                SELECT 'exchange_rate' AS type,
                       e.id,
                       'Валютын ханш тохиргоо' AS title,
                       e.updated_at
                FROM exchange_rate_config e
                WHERE e.updated_at IS NOT NULL
            )
            UNION ALL
            (
                SELECT 'loan_calculator' AS type,
                       lc.id,
                       'Зээлийн тооцоолуур тохиргоо' AS title,
                       lc.updated_at
                FROM loan_calculator_config lc
                WHERE lc.updated_at IS NOT NULL
            )
            ORDER BY updated_at DESC
            LIMIT %s
        """, [limit])

        columns = [col[0] for col in cur.description]
        rows = cur.fetchall()

    # Map type to admin href
    type_href_map = {
        'news': '/admin/news',
        'job': '/admin/hr',
        'service': '/admin/services',
        'exchange_rate': '/admin/rates',
        'loan_calculator': '/admin/calculator',
    }

    type_label_map = {
        'news': 'Мэдээ',
        'job': 'Ажлын зар',
        'service': 'Үйлчилгээ',
        'exchange_rate': 'Валютын ханш',
        'loan_calculator': 'Зээлийн тооцоолуур',
    }

    items = []
    for row in rows:
        item_type = row[0]
        item_id = row[1]
        title = row[2]
        updated_at = row[3]

        items.append({
            'id': f'{item_type}_{item_id}',
            'type': type_label_map.get(item_type, item_type),
            'title': title,
            'href': type_href_map.get(item_type, '/admin'),
            'updatedAt': updated_at.isoformat() if updated_at else None,
        })

    return Response({'items': items})
