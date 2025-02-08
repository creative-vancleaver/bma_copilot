from rest_framework import serializers

from .models import Region, RegionImage, RegionClassification

class RegionImageSerializer(serializers.ModelSerializer):

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = RegionImage
        # exclude = ('region',) # CAN ONLY USE exclude OR fields NOT BOTH.
        fields = ['id', 'image', 'image_url']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
class RegionClassificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = RegionClassification
        exclude = ('region',)

class RegionSerializer(serializers.ModelSerializer):

    # image = RegionImageSerializer(read_only=True, allow_null=True)
    image = RegionImageSerializer(required=False) # ALLOW IMAGE DATA IN PAYLOAD
    classification = RegionClassificationSerializer(read_only=True, allow_null=True)
    case_id = serializers.IntegerField(source='case.id', read_only=True)
    video_id = serializers.IntegerField(source='video.id', read_only=True, allow_null=True)

    class Meta:
        model = Region
        fields = ['id', 'image', 'case_id', 'video_id', 'time_stamp',
                  'TL_x_in_frame', 'TL_y_in_frame', 'BR_x_in_frame',
                  'BR_y_in_frame', 'classification'
                ]
        
    def get_case_id(self, obj):
        return obj.case.id if obj.case else None
    
    def get_video_id(self, obj):
        return obj.video.id if obj.video else None
    
    def create(self, validated_data):
        image_data = validated_data.pop('image', None)
        region = Region.objects.create(**validated_data)

        if image_data:
            RegionImage.objects.create(region=region, **image_data)

        return region
    
    def update(self, instance, validated_data):
        image_data = validated_data.pop('image', None)

        # UPDATE REGION FIELDS
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # UPDATE OR CREATE IMAGE
        if image_data:
            if hasattr(instance, 'image'):
                # UPDATE EXISTING IMAGE
                for attr, value in image_data.items():
                    setattr(instance.image, attr, value)
                instance.image.save()
            else:
                # CREATE NEW IMAGE
                RegionImage.objects.create(region=instance, **image_data)

        return instance