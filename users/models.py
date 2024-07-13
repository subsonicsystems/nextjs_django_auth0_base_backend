from django.db import models


class User(models.Model):
    """ユーザー
    """

    auth0_user_id = models.CharField(max_length=100, db_comment='Auth0ユーザーID')
    first_name = models.CharField(max_length=150, db_comment='名')
    last_name = models.CharField(max_length=150, db_comment='姓')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='作成日時')
    updated_at = models.DateTimeField(auto_now=True, db_comment='更新日時')

    class Meta:
        db_table_comment = 'ユーザー'
