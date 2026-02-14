from rest_framework import serializers
from app.models.models import (
    Product, 
    ProductTranslations, 
    ProductDetails,
    ProductDocument,
    ProductCollaterial,
    ProductCondition,
    Document,
    DocumentTranslation,
    Collateral,
    CollateralTranslation,
    Conditions,
    ConditionTranslations,
    Language
)

class DocumentTranslationNestedSerializer(serializers.ModelSerializer):
    language = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = DocumentTranslation
        fields = ("id", "language", "label")

class DocumentNestedSerializer(serializers.ModelSerializer):
    translations = DocumentTranslationNestedSerializer(
        many=True,
        read_only=True,
        source='documenttranslation_set'
    )
    
    class Meta:
        model = Document
        fields = ("id", "translations")

class CollateralTranslationNestedSerializer(serializers.ModelSerializer):
    language = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = CollateralTranslation
        fields = ("id", "language", "label")

class CollateralNestedSerializer(serializers.ModelSerializer):
    translations = CollateralTranslationNestedSerializer(
        many=True,
        read_only=True,
        source='collateraltranslation_set'
    )
    
    class Meta:
        model = Collateral
        fields = ("id", "translations")

class ConditionTranslationNestedSerializer(serializers.ModelSerializer):
    language = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = ConditionTranslations
        fields = ("id", "language", "label")

class ConditionNestedSerializer(serializers.ModelSerializer):
    translations = ConditionTranslationNestedSerializer(
        many=True,
        read_only=True,
        source='conditiontranslations_set'
    )
    
    class Meta:
        model = Conditions
        fields = ("id", "translations")

class ProductDetailsReadSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        allow_null=True, 
        required=False,
        coerce_to_string=False
    )
    min_fee_percent = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        allow_null=True, 
        required=False,
        coerce_to_string=False
    )
    max_fee_percent = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        allow_null=True, 
        required=False,
        coerce_to_string=False
    )
    min_interest_rate = serializers.DecimalField(
        max_digits=10,  
        decimal_places=2, 
        allow_null=True, 
        required=False,
        coerce_to_string=False
    )
    max_interest_rate = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        allow_null=True, 
        required=False,
        coerce_to_string=False
    )
    
    class Meta:
        model = ProductDetails
        fields = (
            "id",
            "amount",
            "min_fee_percent",
            "max_fee_percent",
            "min_interest_rate",
            "max_interest_rate",
            "term_months",
            "min_processing_hours",
            "max_processing_hoyrs",
            "processing_time_minutes",
            "fee_type",
            "calc_btn_color",
            "calc_btn_font_size",
            "calc_btn_text",
            "request_btn_color",
            "request_btn_font_size",
            "request_btn_text",
            "request_btn_url",
            "disclaimer_color",
            "disclaimer_font_size",
            "disclaimer_text",
        )
class ProductTranslationReadSerializer(serializers.ModelSerializer):
    language = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProductTranslations
        fields = ("id", "language", "label")

class ProductDocumentReadSerializer(serializers.ModelSerializer):
    document = DocumentNestedSerializer(read_only=True)

    class Meta:
        model = ProductDocument
        fields = ("id", "document")

class ProductCollateralReadSerializer(serializers.ModelSerializer):
    collateral = CollateralNestedSerializer(read_only=True)

    class Meta:
        model = ProductCollaterial
        fields = ("id", "collateral")

class ProductConditionReadSerializer(serializers.ModelSerializer):
    condition = ConditionNestedSerializer(read_only=True)

    class Meta:
        model = ProductCondition
        fields = ("id", "condition")

class ProductReadSerializer(serializers.ModelSerializer):
    translations = ProductTranslationReadSerializer(
        many=True,
        read_only=True,
        source='producttranslations_set'
    )
    details = ProductDetailsReadSerializer(
        read_only=True,
        source='productdetails_set',
        many=True
    )
    documents = ProductDocumentReadSerializer(
        many=True,
        read_only=True,
        source='productdocument_set'
    )
    collaterals = ProductCollateralReadSerializer(
        many=True,
        read_only=True,
        source='productcollaterial_set'
    )
    conditions = ProductConditionReadSerializer(
        many=True,
        read_only=True,
        source='productcondition_set'
    )
    product_type = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", 
            "product_type", 
            "translations", 
            "details",
            "documents",
            "collaterals",
            "conditions"
        )