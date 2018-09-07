import requests


class Req():
    def rtn(self, resp):
        if self.to_json:
            return resp.json()
        else:
            return resp.content.decode("UTF-8")

    def get(self, ur):
        ur = self.get_full_url(ur)
        res = requests.get(ur, auth=self.auth_pk, headers=self.h_get)
        return self.rtn(res)

    def post(self, ur, dt=None):
        ur = self.get_full_url(ur)
        if dt is None:
            res = requests.post(ur, auth=self.auth_pk, headers=self.h_post)
        else:
            res = requests.post(ur, auth=self.auth_pk,
                                data=dt, headers=self.h_post)
        return self.rtn(res)

    def put(self, ur, dt=None):
        ur = self.get_full_url(ur)
        if dt is None:
            res = requests.put(ur, auth=self.auth_pk, headers=self.h_post)
        else:
            res = requests.put(ur, auth=self.auth_pk,
                               data=dt, headers=self.h_post)
        return self.rtn(res)

    def delete(self, ur, dt=None):
        ur = self.get_full_url(ur)
        if dt is None:
            res = requests.delete(ur, auth=self.auth_pk, headers=self.h_post)
        else:
            res = requests.delete(ur, auth=self.auth_pk,
                                  data=dt, headers=self.h_post)
        return self.rtn(res)

    def get_full_url(self, url):
        if self.to_json:
            self.query_components.append("format=json")

        if not self.query_components:
            ret = url
        else:
            ret = "{url}?{query}".format(
                url=url, query="&".join(self.query_components))

        self.query_components = []
        return ret


class GroupFolders():
    # /apps/groupfolders/folders
    def getGroupFolders(self):
        return self.get(GroupFolders.url)

    def createGroupFolder(self, mountpoint):
        return self.post(GroupFolders.url, {"mountpoint": mountpoint})

    def deleteGroupFolder(self, fid):
        return self.delete(GroupFolders.url+"/"+str(fid))

    def giveAccessToGroupFolder(self, fid, gid):
        return self.post(GroupFolders.url+"/"+fid+"/"+gid)

    def deleteAccessToGroupFolder(self, fid, gid):
        return self.delete(GroupFolders.url+"/"+fid+"/"+gid)

    def setAccessToGroupFolder(self, fid, gid, permissions):
        return self.post(GroupFolders.url+"/"+fid+"/"+gid, {"permissions": permissions})

    def setQuotaOfGroupFolder(self, fid, quota):
        return self.post(GroupFolders.url+"/"+fid+"/quota", {"quota": quota})

    def renameGroupFolder(self, fid, mountpoint):
        return self.post(GroupFolders.url+"/"+fid+"/mountpoint", {"mountpoint": mountpoint})


class Share():
    # /ocs/v2.php/apps/files_sharing/api/v1
    def getShares(self):
        self.get(Share.url + "/shares")

    def getSharesFromPath(self, path=None, reshares=None, subfiles=None):
        if path is None:
            return False
        url = Share.url + "/shares/" + path

        if reshares is not None:
            self.query_components.append("reshares=true")

        if subfiles is not None:
            self.query_components.append("subfiles=true")

        return self.get(url)

    def getShareInfo(self, sid):
        self.get(Share.url+"/shares/"+sid)

    def createShare(
            self, path, shareType, shareWith=None, publicUpload=None, password=None,
            permissions=None):
        url = Share.url + "/shares"
        if publicUpload:
            publicUpload = "true"
        if (path is None or isinstance(shareType, int) != True) or (shareType in [0, 1] and shareWith is None):
            return False
        msg = {"path": path, "shareType": shareType}
        if shareType in [0, 1]:
            msg["shareWith"] = shareWith
        if publicUpload:
            msg["publicUpload"] = publicUpload
        if shareType == 3 and password is not None:
            msg["password"] = str(password)
        if permissions is not None:
            msg["permissions"] = permissions
        return self.post(url, msg)

    def deleteShare(self, sid):
        return self.delete(Share.url+"/shares/"+sid)

    def updateShare(self, sid, permissions=None, password=None, publicUpload=None, expireDate=None):
        if permissions is None and password is None and publicUpload is None and expireDate is None:
            return False
        msg = {}
        if permissions is not None:
            msg["permissions"] = permissions
        if password is not None:
            msg["password"] = str(password)
        if publicUpload:
            msg["publicUpload"] = "true"
        if publicUpload is False:
            msg["publicUpload"] = "false"
        if expireDate is not None:
            msg["expireDate"] = expireDate
        return self.put(Share.url+"/shares/"+sid, msg)

    def listAcceptedFederatedCloudShares(self):
        return self.get(Share.url+"/remote_shares")

    def getKnownFederatedCloudShare(self, sid):
        return self.get(Share.url+"/remote_shares/"+str(sid))

    def deleteAcceptedFederatedCloudShare(self, sid):
        return self.delete(Share.url+"/remote_shares/"+str(sid))

    def listPendingFederatedCloudShares(self, sid):
        return self.get(Share.url+"/remote_shares/pending")

    def acceptPendingFederatedCloudShare(self, sid):
        return self.post(Share.url+"/remote_shares/pending/"+str(sid))

    def declinePendingFederatedCloudShare(self, sid):
        return self.delete(Share.url+"/remote_shares/pending/"+str(sid))


class Apps():
    # /ocs/v1.php/cloud/apps
    def getApps(self, filter=None):
        if filter is True:
            self.query_components.append("filter=enabled")
        elif filter is False:
            self.query_components.append("filter=disabled")
        return self.get(Apps.url)

    def getApp(self, aid):
        return self.get(Apps.url + "/" + aid)

    def enableApp(self, aid):
        return self.post(Apps.url + "/" + aid)

    def disableApp(self, aid):
        return self.delete(Apps.url + "/" + aid)


class Group():
    # /ocs/v1.php/cloud/groups
    def getGroups(self, search=None, limit=None, offset=None):
        url = Group.url
        if search is not None or limit is not None or offset is not None:
            if search is not None:
                self.query_components.append("search=%s" % search)
            if limit is not None:
                self.query_components.append("limit=%s" % limit)
            if offset is not None:
                self.query_components.append("offset=%s" % offset)
        return self.get(url)

    def addGroup(self, gid):
        url = Group.url
        msg = {"groupid": gid}
        return self.post(url, msg)

    def getGroup(self, gid):
        return self.get(Group.url + "/" + gid)

    def getSubAdmins(self, gid):
        return self.get(Group.url + "/" + gid + "/subadmins")

    def deleteGroup(self, gid):
        return self.delete(Group.url + "/" + gid)


class User():
    # /ocs/v1.php/cloud/users
    def addUser(self, uid, passwd):
        msg = {'userid': uid, 'password': passwd}
        return self.post(User.url, msg)

    def getUsers(self, search=None, limit=None, offset=None):
        url = User.url
        if search is not None or limit is not None or offset is not None:
            url += "?"
            if search is not None:
                self.query_components.append("search=%s" % search)
            if limit is not None:
                self.query_components.append("limit=%s" % limit)
            if offset is not None:
                self.query_components.append("offset=%s" % offset)
        return self.get(url)

    def getUser(self, uid):
        return self.get(User.url + "/" + uid)

    def editUser(
            self, uid, email=None, quota=None, displayname=None, phone=None, address=None,
            website=None, twitter=None, password=None):
        url = User.url + "/" + uid
        msg = {}
        if email is not None:
            msg = {'key': "email", 'value': email}
            self.put(url, msg)
        if quota is not None:
            msg = {'key': "quota", 'value': quota}
            self.put(url, msg)
        if phone is not None:
            msg = {'key': "phone", 'value': phone}
            self.put(url, msg)
        if address is not None:
            msg = {'key': "address", 'value': address}
            self.put(url, msg)
        if website is not None:
            msg = {'key': "website", 'value': website}
            self.put(url, msg)
        if twitter is not None:
            msg = {'key': "twitter", 'value': twitter}
            self.put(url, msg)
        if displayname is not None:
            msg = {'key': "displayname", 'value': displayname}
            self.put(url, msg)
        if password is not None:
            msg = {'key': "password", 'value': password}
            self.put(url, msg)
        if msg != {}:
            return True
        else:
            return False

    def disableUser(self, uid):
        return self.put(User.url + "/" + uid + "/disable")

    def enableUser(self, uid):
        return self.put(User.url + "/" + uid + "/enable")

    def deleteUser(self, uid):
        return self.delete(User.url + "/" + uid)

    def addToGroup(self, uid, gid):
        url = User.url + "/" + uid + "/groups"
        msg = {'groupid': gid}
        return self.post(url, msg)

    def removeFromGroup(self, uid, gid):
        url = User.url + "/" + uid + "/groups"
        msg = {'groupid': gid}
        return self.delete(url, msg)

    def createSubAdmin(self, uid, gid):
        url = User.url + "/" + uid + "/subadmins"
        msg = {'groupid': gid}
        return self.post(url, msg)

    def removeSubAdmin(self, uid, gid):
        url = User.url + "/" + uid + "/subadmins"
        msg = {'groupid': gid}
        return self.delete(url, msg)

    def getSubAdminGroups(self, uid):
        return self.get(User.url + "/" + uid + "/subadmins")

    def resendWelcomeMail(self, uid):
        return self.post(User.url + "/" + uid + "/welcome")


class NextCloud(Req, User, Group, Apps, Share, GroupFolders):
    '''
    OCS StatusCode
        100 - successful
        996 - server error
        997 - not authorized
        998 - not found
        999 - unknown error
    Parameters
        uid -> UserID(UserName)
        gid -> GroupID(GroupName)
        aid -> AppID(ApplicationName)
        sid -> ShareID
        fid -> FolderID

        Quota
            -3 -> Unlimited
        ShareType
            0 -> user
            1 -> group
            3 -> publicLink
            6 -> federated cloud share
        Permissions
            1  -> read
            2  -> update
            4  -> create
            8  -> delete
            16 -> share
            31 -> all
        expireDate -> String e.g "YYYY-MM-DD"
    '''

    def __init__(self, endpoint, user, passwd, js=False):
        self.query_components = []

        self.to_json = js

        self.endpoint = endpoint
        User.url = endpoint + "/ocs/v1.php/cloud/users"
        Group.url = endpoint + "/ocs/v1.php/cloud/groups"
        Share.url = endpoint + "/ocs/v2.php/apps/files_sharing/api/v1"
        Apps.url = endpoint + "/ocs/v1.php/cloud/apps"
        # GroupFolders.url = endpoint + "/ocs/v2.php/apps/groupfolders/folders"
        GroupFolders.url = endpoint + "/apps/groupfolders/folders"
        self.h_get = {"OCS-APIRequest": "true"}
        self.h_post = {"OCS-APIRequest": "true",
                       "Content-Type": "application/x-www-form-urlencoded"}
        self.auth_pk = (user, passwd)
