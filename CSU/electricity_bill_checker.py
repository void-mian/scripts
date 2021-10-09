from datetime import datetime
import logging
import base64
from sys import argv, stderr
import dateutil.parser
import dateutil.tz
from urllib import request, parse
from bs4 import BeautifulSoup


class BillChecker:
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}

    def __init__(self, UserAccount: str, Password: str, cookie: str = None):
        """
        Check Electricity Bill in CSU

        Args:
            UserAccount: SchoolCard ID (校园卡账号)
            Password: SchoolCard Query Password (校园卡查询密码)
            cookie: Cookie
        """
        self.UserAccount = UserAccount
        self.Password = Password
        self.cookie = cookie

    def login(self):
        """
        Login and get cookie.
        """
        url = 'http://ecard.csu.edu.cn:8070/Account/Login'
        data = {'SignType': 'SynCard', 'UserAccount': self.UserAccount,
                'Password': base64.b64encode(self.Password.encode('utf-8')).decode('utf-8')}
        data = parse.urlencode(data).encode('utf-8')
        req = request.Request(url, data=data, headers=BillChecker.header)
        res = request.urlopen(req)
        self.cookie = res.headers.get('Set-Cookie')
        logging.info('[login info]: ' + res.read().decode('utf-8'))
        logging.info('[cookie]: ' + self.cookie)

    def expires(self) -> bool:
        """
        Check if cookie is expired or not.

        Returns:
            expired or not
        """
        if (self.cookie is None) or ('expires' not in self.cookie):
            return True
        try:
            date = dict((k.strip(), v.strip())
                        for k, v in (c.split('=') for c in self.cookie.split(';')))['expires']
            expire = dateutil.parser.parse(
                date).astimezone(dateutil.tz.tzutc())
            now = datetime.now().astimezone(dateutil.tz.tzutc())
            return expire <= now
        except (ValueError, KeyError):
            return True

    def check(self) -> str:
        """
        Check the electricity bill.

        Returns:
            Electricity bill balance
        """
        if self.expires():
            self.login()
        url = 'http://ecard.csu.edu.cn:8070/AutoPay/PowerFee/CsuIndex'
        req = request.Request(url, headers=BillChecker.header)
        req.add_header('Cookie', self.cookie)
        res = request.urlopen(req)
        soup = BeautifulSoup(res, 'lxml')
        return soup.find('span', {'id': 'getbanlse'}).text.strip()


if __name__ == '__main__':
    if len(argv)-1 != 2:
        print('Usage: python3 '+argv[0] +
              ' SchoolCardID QueryPassword', file=stderr)
        exit(-1)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    bc = BillChecker(argv[1], argv[2])
    print('Electricity bill balance:', bc.check(), 'CNY')
