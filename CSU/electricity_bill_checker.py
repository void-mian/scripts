from datetime import datetime
import logging
import base64
from sys import argv, stderr
import dateutil.parser
import dateutil.tz
from urllib import request, parse
from bs4 import BeautifulSoup
import argparse


class BillChecker:
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}
    info = {
        'xiaoqu': ('xiaoquName', {'build': 'buildName'}),
        '02': ('南校区', {
            '01': '升华公寓1栋南',
            '02': '升华公寓1栋北',
            '03': '升华公寓2栋',
            '04': '升华公寓3栋',
            '05': '升华公寓4栋',
            '06': '升华公寓5栋',
            '07': '升华公寓6栋',
            '08': '升华公寓7栋',
            '09': '升华公寓8栋',
            '10': '升华公寓9栋',
            '11': '升华公寓10栋',
            '12': '升华公寓11栋',
            '13': '升华公寓12栋',
            '14': '升华公寓13栋',
            '15': '升华公寓14栋',
            '16': '升华公寓15栋',
            '17': '升华公寓16栋',
            '18': '升华公寓17栋',
            '19': '升华公寓18栋',
            '20': '升华公寓19栋',
            '21': '升华公寓20栋',
            '22': '升华公寓21栋',
            '23': '升华公寓24栋',
            '24': '升华公寓25栋',
            '25': '升华公寓26栋',
            '26': '升华公寓27栋',
            '27': '升华公寓28栋南',
            '28': '升华公寓28栋北',
            '29': '升华公寓29栋',
            '30': '升华公寓30栋',
            '31': '升华公寓31栋',
            '32': '升华公寓32栋',
            '33': '升华公寓33栋',
            '34': '南校区5舍',
            '35': '南校区6舍',
            '36': '南校区8舍',
        }),
        '03': ('铁道校区', {
            '01': '铁道校区学生1舍',
            '02': '铁道校区学生2舍',
            '03': '铁道校区学生3舍',
            '05': '铁道校区学生新5舍',
            '06': '铁道校区学生新6舍',
            '07': '铁道校区学生10舍',
            '08': '铁道校区学生11舍',
            '09': '铁道校区新1舍',
            '10': '铁道校区新2舍',
            '11': '铁道校区新3舍',
            '12': '铁道校区留5舍',
            '12': '铁道校区研究生楼',
            '13': '铁道校区留1舍',
            '14': '铁道校区留7舍',
            '15': '铁道校区留2舍',
            '16': '铁道校区留3舍',
        }),
        '04': ('湘雅新校区', {
            '01': '湘雅新校区1号楼',
            '02': '湘雅新校区2号楼',
            '03': '湘雅新校区3号楼',
            '04': '湘雅新校区4号楼',
            '05': '湘雅新校区5号楼',
            '06': '湘雅新校区6号楼',
            '07': '湘雅新校区7号楼',
        }),
        '05': ('湘雅老校区', {
            '01': '湘雅老校区研1舍',
            '02': '湘雅老校区研2舍',
            '03': '湘雅老校区研3舍',
            '04': '湘雅老校区成教楼',
            '05': '湘雅老校区A栋',
            '06': '湘雅老校区B栋',
        }),
        '12': ('升华校区留学生宿舍', {
            '01': '升华校区留学生1舍',
            '02': '升华校区留学生2舍',
        }),
        '13': ('铁道新123舍', {
            '01': '铁道校区学生新1舍',
            '02': '铁道校区学生新2舍',
            '03': '铁道校区学生新3舍',
        }),
    }

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
        req = request.Request(url, data=parse.urlencode({'SignType': 'SynCard', 'UserAccount': self.UserAccount,
                                                         'Password': base64.b64encode(self.Password.encode('utf-8')).decode('utf-8')}).encode('utf-8'), headers=BillChecker.header)
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

    def pay(self, room: str, amount: int) -> str:
        """
        Args:
            room: room = xiaoqu+build+'-'+roomid
                  example: 0101-0101
            amount: how much to pay
        """
        if self.expires():
            self.login()
        url = 'http://ecard.csu.edu.cn:8070/Api/PowerFee/DoPowerPay'
        req = request.Request(url, headers=BillChecker.header, data=parse.urlencode({'paytypeCode': 'Yima',
                                                                                     'clientType': 'webapp',
                                                                                     'pwd': base64.b64encode(self.Password.encode('utf-8')).decode('utf-8'),
                                                                                     'xiaoqu': room.split('-')[0][:2],
                                                                                     'xiaoquName': BillChecker.info[room.split('-')[0][:2]][0],
                                                                                     'build': room.split('-')[0][2:],
                                                                                     'buildName': BillChecker.info[room.split('-')[0][:2]][1][room.split('-')[0][2:]],
                                                                                     'room': room,
                                                                                     'amount': str(amount),
                                                                                     }).encode('utf-8'))
        req.add_header('Cookie', self.cookie)
        res = request.urlopen(req)
        soup = BeautifulSoup(res, 'lxml')
        if soup.find('label', {'id': 'errorMsg'}) is not None:
            return soup.find('label', {'id': 'errorMsg'}).text.strip()
        else:
            return soup.find('p').text.strip()


class Parser:
    def check(args):
        bc = BillChecker(args.SchoolCardID, args.QueryPassword)
        print('Electricity bill balance:', bc.check(), 'CNY')

    def pay(args):
        bc = BillChecker(args.SchoolCardID, args.QueryPassword)
        print('Electricity bill balance:', bc.check(), 'CNY')
        print('Payment result:', bc.pay(args.room, args.amount))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    check = subparsers.add_parser('check')
    check.add_argument('--SchoolCardID', '-u', type=str, required=True)
    check.add_argument('--QueryPassword', '-p', type=str, required=True)
    check.set_defaults(func=Parser.check)
    pay = subparsers.add_parser('pay')
    pay.add_argument('--SchoolCardID', '-u', type=str, required=True)
    pay.add_argument('--QueryPassword', '-p', type=str, required=True)
    pay.add_argument('--room', '-r', type=str, required=True)
    pay.add_argument('amount', type=int)
    pay.set_defaults(func=Parser.pay)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    args = parser.parse_args()
    args.func(args)
