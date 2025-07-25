from django.contrib import admin
from .models import GPTRuleQA, FinetuningRuleQA

# Register your models here.
@admin.register(GPTRuleQA)
class GPTRuleQAAdmin(admin.ModelAdmin):
    list_display = ['id', 'game_name', 'question_preview', 'created_at']
    list_filter = ['game_name', 'created_at']
    search_fields = ['game_name', 'question', 'answer']
    ordering = ['-created_at']
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = '질문'

@admin.register(FinetuningRuleQA)
class FinetuningRuleQAAdmin(admin.ModelAdmin):
    list_display = ['id', 'game_name', 'question_preview', 'created_at']
    list_filter = ['game_name', 'created_at']
    search_fields = ['game_name', 'question', 'answer']
    ordering = ['-created_at']
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = '질문'
