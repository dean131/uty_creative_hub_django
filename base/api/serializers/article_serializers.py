from rest_framework import serializers
from base.api.serializers.articleimage_serializers import ArticleImageSerializer

from base.models import Article


class ArticleListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = [
            'article_id', 
            'article_type', 
            'article_title', 
            'article_body', 
            'article_link', 
            'time_since',
            'image',
        ]

    def get_image(self, obj):
        image = obj.articleimage_set.first()
        if image:
            return ArticleImageSerializer(image, context=self.context).data.get('article_image')
        return None


class ArticleSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = [
            'article_id', 
            'article_type', 
            'article_title', 
            'article_body', 
            'article_link', 
            'created_at', 
            'time_since',
            'formated_created_at',
            'images',
        ]

    def get_images(self, obj):
        images = obj.articleimage_set.all()
        if images:
            return ArticleImageSerializer(images, many=True, context=self.context).data
        return None