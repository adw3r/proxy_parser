from unittest import TestCase

from proxy_parser.checkers import check_proxy, check_proxy_list

TEST_PROXIES_SOURCE = 'https://github.com/keyaanminhas/ka4mas_inventory/raw/1fce10b92fb9f8b38d5f11315bdcb8f15788fb7d/GMAIL/config/proxies.txt'
TEST_PROXY_LIST = (
    'http://132.145.210.43:3128',
    'http://134.236.41.59:8080',
    'http://186.48.36.142:8080',
    'http://103.47.175.161:83',
    'http://36.90.92.219:8080',
    'http://89.43.31.134:3128',
    'http://102.141.162.116:8080',
    'http://83.171.236.79:8080',
    'http://41.186.44.106:3128',
    'http://45.156.29.3:9090',
    'http://111.225.153.37:8089',
    'http://194.87.188.114:8000',
    'http://54.219.166.195:3128',
    'http://101.109.235.46:8080',
    'http://202.131.159.230:1111',
    'http://177.136.218.105:8080',
    'http://103.148.23.22:8080',
    'http://45.156.29.97:9090',
    'http://23.239.7.212:3128',
    'http://165.16.27.35:1981',
    'http://200.106.187.242:999',
    'http://209.250.236.93:8080',
    'http://200.24.134.61:999',
    'http://91.225.242.5:8080',
    'http://145.40.121.15:3128',
    'http://78.47.153.18:8080',
    'http://35.204.215.95:3128',
    'http://117.102.70.42:8080',
    'http://216.238.66.39:3128',
    'http://187.58.239.154:8080',
    'http://47.89.241.242:80',
    'http://180.234.166.31:8080',
    'http://112.133.231.132:8000',
    'http://196.2.15.159:8080',
    'http://134.236.8.253:8080',
    'http://46.227.247.87:8080',
)
TEST_PROXY = 'http://46.227.247.87:8080'


class TestChecker(TestCase):

    def test_proxy_checker(self):

        proxy_checked = check_proxy(TEST_PROXY)
        self.assertIsNotNone(proxy_checked)

    def test_proxy_list(self):
        for proxy in check_proxy_list(set(TEST_PROXY_LIST)):
            print(proxy)
