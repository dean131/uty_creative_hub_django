from rest_framework import serializers

from base.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'article_id', 
            'article_type', 
            'article_title', 
            'article_body', 
            'article_image', 
            'article_link', 
            'created_at', 
            'time_since'
        ]