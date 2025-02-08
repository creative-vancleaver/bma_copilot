from rest_framework import serializers

from .models import Cell, CellDetection, CellClassification

class CellDetectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CellDetection
        exclude = ('cell',) # EXCLUDE CELL TO AVOID CIRCULAR REFERENCE

class CellClassificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CellClassification
        exclude = ('cell',)

class CellSerializer(serializers.ModelSerializer):

    detection = CellDetectionSerializer(read_only=True, allow_null=True)
    classification = CellClassificationSerializer(read_only=True, allow_null=True)
    image_url = serializers.SerializerMethodField()
    case_id = serializers.SerializerMethodField()
    region_id = serializers.IntegerField(source='region.id', read_only=True)

    class Meta:
        model = Cell
        # fields = '__all__'
        fields = [
            'id', 'image', 'image_url', 'case_id', 'region_id',
            'center_x_in_region', 'center_y_in_region',
            'TL_x_in_region', 'TL_y_in_region',
            'BR_x_in_region', 'BR_y_in_region',
            'detection', 'classification'
        ]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_case_id(self, obj):
        return obj.region.case_id if obj.region else None
