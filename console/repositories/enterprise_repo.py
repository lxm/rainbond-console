# -*- coding: utf-8 -*-
import logging

from django.db.models import Q

from console.models.main import EnterpriseUserPerm
from console.repositories.base import BaseConnection
from www.models.main import TenantEnterprise

logger = logging.getLogger("default")


class TenantEnterpriseRepo(object):
    def get_enterprise_by_enterprise_name(self, enterprise_name):
        enterprise = TenantEnterprise.objects.filter(enterprise_name=enterprise_name)
        if not enterprise:
            return None
        else:
            return enterprise[0]

    def get_enterprise_first(self):
        """
        获取第一条企业名
        :return:
        """
        enterprise = TenantEnterprise.objects.first()
        if not enterprise:
            return None
        else:
            return enterprise

    def get_enterprise_by_enterprise_id(self, enterprise_id, exception=True):
        enterprise = TenantEnterprise.objects.filter(enterprise_id=enterprise_id)
        if not enterprise:
            return None
        else:
            return enterprise[0]

    def create_enterprise(self, **params):
        return TenantEnterprise.objects.create(**params)

    def get_enterprises_by_enterprise_ids(self, eids):
        return TenantEnterprise.objects.filter(enterprise_id__in=eids)

    def get_by_enterprise_alias(self, enterprise_alias):
        return TenantEnterprise.objects.filter(enterprise_alias=enterprise_alias).first()

    def list_all(self, query):
        if query:
            return TenantEnterprise.objects.filter(Q(enterprise_name__contains=query) |
                                                   Q(enterprise_alias__contains=query)).all()
        return TenantEnterprise.objects.all()

    def update(self, eid, **data):
        TenantEnterprise.objects.filter(enterprise_id=eid).update(**data)

    def list_appstore_infos(self, query="", page=None, page_size=None):
        limit = ""
        if page is not None and page_size is not None:
            page = page if page > 0 else 1
            page = (page - 1) * page_size
            limit = "Limit {page}, {size}".format(page=page, size=page_size)
        where = ""
        if query:
            where = "WHERE a.enterprise_alias LIKE '%{query}%' OR a.enterprise_name LIKE '%{query}%'".format(
                query=query)
        sql = """
        SELECT
            a.enterprise_id,
            a.enterprise_name,
            a.enterprise_alias,
            b.access_url
        FROM
            tenant_enterprise a
            JOIN tenant_enterprise_token b ON a.id = b.enterprise_id
        {where}
        {limit}
        """.format(where=where, limit=limit)

        conn = BaseConnection()
        result = conn.query(sql)
        return result

    def count_appstore_infos(self, query=""):
        where = ""
        if query:
            where = "WHERE a.enterprise_alias LIKE '%{query}%' OR a.enterprise_name LIKE '%{query}%'".format(
                query=query)
        sql = """
        SELECT
            count(*) as total
        FROM
            tenant_enterprise a
            JOIN tenant_enterprise_token b ON a.id = b.enterprise_id
        {where}
        """.format(where=where)

        conn = BaseConnection()
        result = conn.query(sql)
        return result[0]["total"]


class TenantEnterpriseUserPermRepo(object):
    def create_enterprise_user_perm(self, user_id, enterprise_id, identity, token=None):
        if token is None:
            return EnterpriseUserPerm.objects.create(user_id=user_id, enterprise_id=enterprise_id, identity=identity)
        else:
            return EnterpriseUserPerm.objects.create(
                user_id=user_id, enterprise_id=enterprise_id, identity=identity, token=token)

    def get_user_enterprise_perm(self, user_id, enterprise_id):
        return EnterpriseUserPerm.objects.filter(user_id=user_id, enterprise_id=enterprise_id)

    def get_backend_enterprise_admin_by_user_id(self, user_id):
        """
        管理后台查询企业管理员，只有一个企业
        :param user_id:
        :param enterprise_id:
        :return:
        """
        enter_admin = EnterpriseUserPerm.objects.filter(user_id=user_id).first()
        if enter_admin:
            return enter_admin
        else:
            return None

    def count_by_eid(self, eid):
        return EnterpriseUserPerm.objects.filter(enterprise_id=eid).count()

    def delete_backend_enterprise_admin_by_user_id(self, user_id):
        """
        管理后台删除企业管理员，只有一个企业
        :param user_id:
        :param enterprise_id:
        :return:
        """
        EnterpriseUserPerm.objects.filter(user_id=user_id).delete()

    def get_by_token(self, token):
        return EnterpriseUserPerm.objects.filter(token=token).first()


enterprise_repo = TenantEnterpriseRepo()
enterprise_user_perm_repo = TenantEnterpriseUserPermRepo()
