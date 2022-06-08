import requests
import myTool
import execjs
import time


class Sh:
    def __init__(self):
        self.get_img_url = 'https://etax.shanxi.chinatax.gov.cn/gzfw/common/captcha/get'
        self.check_url = 'https://etax.shanxi.chinatax.gov.cn/gzfw/common/captcha/check'
        self.query_url = 'https://etax.shanxi.chinatax.gov.cn/gzfw/myCommonRemote/commonQuery'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
        }

        self.session = requests.Session()
        self.session.headers.update(headers)

        self.captchaType = 'blockPuzzle'
        self.clientUid = 'slider-1a6d1596-6001-4604-98a0-6772c3836adb'

    def post(self, url, data):
        resp = self.session.post(url, json=data, timeout=5)
        return resp

    def ts(self):
        return int(time.time() * 1000)

    def get_repData(self):
        data = {
            'captchaType': self.captchaType,
            'clientUid': self.clientUid,
            'ts': self.ts()
        }
        resp = self.post(self.get_img_url, data)
        repData = resp.json()['repData']

        return repData

    def get_x(self, jigsawImage, originalImage):
        x = myTool.detectDistanceX(originalImage, jigsawImage)

        return x

    def check(self, token, pointJson):
        data = {
            'captchaType': self.captchaType,
            'clientUid': self.clientUid,
            'ts': self.ts(),
            'token': token,
            'pointJson': pointJson
        }
        resp = self.post(self.check_url, data)

        return resp.json()['success']

    def get_pointJson(self, secretKey, x):
        # x = x * 310 / 400
        word = f'{{"x":{x},"y":5}}'
        with open('shanxi.js') as f:
            jsText = f.read()
        js = execjs.compile(jsText)
        pointJson = js.call('AES_Encrypt', word, secretKey)

        return pointJson

    def get_captchaVerification(self, secretKey, token, x):
        word = f'{token}---{{"x":{x},"y":5}}'
        with open('shanxi.js') as f:
            jsText = f.read()
        js = execjs.compile(jsText)
        pointJson = js.call('AES_Encrypt', word, secretKey)

        return pointJson

    def query(self, nsrsbh, captchaVerification):
        params = {
            "sqlid": "OnlineSearch_nsrzt",
            "flag": "captcha",
            "captchaVerification": captchaVerification
        }
        data = {
            "HPLXR": "",
            "HPLXRDH": "",
            "HPSFZJLX_DM": "201",
            "HPSFZJHM": "",
            "LXR": "",
            "LXRDH": "",
            "SFZJLX_DM": "201",
            "SFZJHM": "",
            "NSR": nsrsbh,
            "_search": "false",
            "nd": self.ts(),
            "limit": "50",
            "page": "1",
            "sidx": "",
            "sord": "asc"
        }
        resp = self.session.post(self.query_url, params=params, data=data, timeout=5)
        for i in resp.json()['message']:
            print(i)

    def run(self, nsrsbh):
        repData = self.get_repData()
        jigsawImage = myTool.b64decode(repData['jigsawImageBase64'])
        originalImage = myTool.b64decode(repData['originalImageBase64'])
        x = self.get_x(jigsawImage, originalImage)
        secretKey = repData['secretKey']
        token = repData['token']
        pointJson = self.get_pointJson(secretKey, x)
        if self.check(token, pointJson):
            captchaVerification = self.get_captchaVerification(secretKey, token, x)
            self.query(nsrsbh, captchaVerification)

if __name__ == '__main__':
    s = Sh()
    s.run('91140521MA0K72GP5W')
