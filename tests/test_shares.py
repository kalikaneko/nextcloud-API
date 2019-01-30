import requests
from datetime import datetime, timedelta

from .base import BaseTestCase, NextCloud, NEXTCLOUD_URL

from NextCloud.base import ShareType, Permission, datetime_to_expire_date


class TestShares(BaseTestCase):

    def setUp(self):
        super(TestShares, self).setUp()
        user_password = self.get_random_string(length=8)
        self.user_username = self.create_new_user('shares_user_', password=user_password)
        self.nxc_local = self.nxc_local = NextCloud(NEXTCLOUD_URL, self.user_username, user_password, json_output=True)
        # make user admin
        self.nxc.add_to_group(self.user_username, 'admin')

    def tearDown(self):
        self.nxc.delete_user(self.user_username)

    def test_share_create_retrieve_delete(self):
        """ shallow test for base retrieving single, list, creating and deleting share """
        # check no shares exists
        res = self.nxc_local.get_shares()
        assert res['ocs']['meta']['statuscode'] == self.SHARE_API_SUCCESS_CODE
        assert len(res['ocs']['data']) == 0

        # create public share
        res = self.nxc_local.create_share('Documents', share_type=ShareType.PUBLIC_LINK.value)
        assert res['ocs']['meta']['statuscode'] == self.SHARE_API_SUCCESS_CODE
        share_id = res['ocs']['data']['id']

        # get all shares
        all_shares = self.nxc_local.get_shares()['ocs']['data']
        assert len(all_shares) == 1
        assert all_shares[0]['id'] == share_id
        assert all_shares[0]['share_type'] == ShareType.PUBLIC_LINK.value

        # get single share info
        created_share = self.nxc_local.get_share_info(share_id)
        assert res['ocs']['meta']['statuscode'] == self.SHARE_API_SUCCESS_CODE
        created_share_data = created_share['ocs']['data'][0]
        assert created_share_data['id'] == share_id
        assert created_share_data['share_type'] == ShareType.PUBLIC_LINK.value
        assert created_share_data['uid_owner'] == self.user_username

        # delete share
        res = self.nxc_local.delete_share(share_id)
        assert res['ocs']['meta']['statuscode'] == self.SHARE_API_SUCCESS_CODE
        all_shares = self.nxc_local.get_shares()['ocs']['data']
        assert len(all_shares) == 0

    def test_create(self):
        """ creating share with different params """
        share_path = "Documents"
        user_to_share_with = self.create_new_user("test_shares_")
        group_to_share_with = 'group_to_share_with'
        self.nxc.add_group(group_to_share_with)

        # create for user, group
        for (share_type, share_with, permissions) in [(ShareType.USER.value, user_to_share_with, Permission.READ.value),
                                                      (ShareType.GROUP.value, group_to_share_with, Permission.READ.value + Permission.CREATE.value)]:
            # create share with user
            res = self.nxc_local.create_share(share_path,
                                              share_type=share_type,
                                              share_with=share_with,
                                              permissions=permissions)
            assert res['ocs']['meta']['statuscode'] == self.SHARE_API_SUCCESS_CODE
            share_id = res['ocs']['data']['id']

            # check if shared with right user/group, permission
            created_share = self.nxc_local.get_share_info(share_id)
            assert res['ocs']['meta']['statuscode'] == self.SHARE_API_SUCCESS_CODE
            created_share_data = created_share['ocs']['data'][0]
            assert created_share_data['id'] == share_id
            assert created_share_data['share_type'] == share_type
            assert created_share_data['share_with'] == share_with
            assert created_share_data['permissions'] == permissions

            # delete share, user
            self.nxc_local.delete_share(share_id)
            self.nxc.delete_user(user_to_share_with)

    def test_create_with_password(self):
        share_path = "Documents"
        res = self.nxc_local.create_share(path=share_path,
                                          share_type=ShareType.PUBLIC_LINK.value,
                                          password=self.get_random_string(length=8))
        assert res['ocs']['meta']['statuscode'] == self.SHARE_API_SUCCESS_CODE
        share_url = res['ocs']['data']['url']
        share_resp = requests.get(share_url)
        assert "This share is password-protected" in share_resp.text
        self.nxc_local.delete_share(res['ocs']['data']['id'])

    def test_get_path_shares(self):
        share_path = "Documents"
        group_to_share_with_name = self.get_random_string(length=4) + "_test_add"
        self.nxc.add_group(group_to_share_with_name)

        # check that path has no shares yet
        res = self.nxc_local.get_shares_from_path(share_path)
        assert res['ocs']['meta']['statuscode'] == self.SHARE_API_SUCCESS_CODE
        assert len(res['ocs']['data']) == 0

        # first path share
        first_share = self.nxc_local.create_share(path=share_path,
                                                  share_type=ShareType.PUBLIC_LINK.value)

        # create second path share
        second_share = self.nxc_local.create_share(path=share_path,
                                                   share_type=ShareType.GROUP.value,
                                                   share_with=group_to_share_with_name,
                                                   permissions=Permission.READ.value)

        all_shares_ids = [first_share['ocs']['data']['id'], second_share['ocs']['data']['id']]

        # check that path has two shares
        res = self.nxc_local.get_shares_from_path(share_path)
        assert res['ocs']['meta']['statuscode'] == self.SHARE_API_SUCCESS_CODE
        assert len(res['ocs']['data']) == 2
        assert all([each['id'] in all_shares_ids for each in res['ocs']['data']])

        # clean shares, groups
        self.clear(self.nxc_local, share_ids=all_shares_ids, group_ids=[group_to_share_with_name])

    def test_update_share(self):
        share_path = "Documents"
        user_to_share_with = self.create_new_user("test_shares_")

        share_with = user_to_share_with
        share_type = ShareType.USER.value
        # create share with user
        res = self.nxc_local.create_share(share_path,
                                          share_type=ShareType.USER.value,
                                          share_with=user_to_share_with,
                                          permissions=Permission.READ.value)
        assert res['ocs']['meta']['statuscode'] == self.SHARE_API_SUCCESS_CODE
        share_id = res['ocs']['data']['id']

        # update share permissions
        new_permissions = Permission.READ.value + Permission.CREATE.value
        res = self.nxc_local.update_share(share_id, permissions=new_permissions)
        assert res['ocs']['meta']['statuscode'] == self.SHARE_API_SUCCESS_CODE

        updated_share_data = res['ocs']['data']
        assert updated_share_data['id'] == share_id
        assert updated_share_data['share_type'] == share_type
        assert updated_share_data['share_with'] == share_with
        assert updated_share_data['permissions'] == new_permissions
        assert updated_share_data['expiration'] is None

        # update share expire date
        expire_date = datetime_to_expire_date(datetime.now() + timedelta(days=5))
        res = self.nxc_local.update_share(share_id, expire_date=expire_date)
        assert res['ocs']['meta']['statuscode'] == self.SHARE_API_SUCCESS_CODE

        updated_share_data = res['ocs']['data']
        assert updated_share_data['id'] == share_id
        assert updated_share_data['share_type'] == share_type
        assert updated_share_data['share_with'] == share_with
        assert updated_share_data['permissions'] == new_permissions
        assert updated_share_data['expiration'] == "{} 00:00:00".format(expire_date)

        self.clear(self.nxc_local, share_ids=[share_id], user_ids=[user_to_share_with])
