import urllib.request as rq

def set_digest_auth(uri, username, password):
    # uri = f'{request.host_url}secret'
    pass_mgr = rq.HTTPPasswordMgrWithDefaultRealm()
    pass_mgr.add_password(realm=None, uri=uri, user=username, passwd=password)
    auth_handler = rq.HTTPDigestAuthHandler(pass_mgr)
    opener = rq.build_opener(auth_handler)
    rq.install_opener(opener)

uri = "http://leggiero.sakura.ne.jp/xxxxbasic_auth_testxxxx/secret/kaiin.htm"
user = "kaiin"
passwd = "naisho"

set_digest_auth(uri, user, passwd)
res = rq.urlopen(uri)

print("status = {0}".format(res.status))
