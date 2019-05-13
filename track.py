import requests
import json
import execjs
import socket  # 内置库
import socks  # 需要安装：pip install pysocks
import time
import schedule
import logging


class Track(object):

    def track17(self):

        log_format = "%(asctime)s - %(levelname)s - %(message)s"  # 日志输出格式
        logging.basicConfig(filename='tracklog.log', filemode='a', level=logging.DEBUG, format=log_format)
        try:
            # 代理服务器IP（域名）
            socks5_proxy_host = '204.12.207.146'
            # 代理服务器端口号
            socks5_proxy_port = 24000

            # 设置代理
            socks.set_default_proxy(socks.SOCKS5, socks5_proxy_host, socks5_proxy_port)
            socket.socket = socks.socksocket
        except Exception as e:
            logging.debug(e, '代理ip出现问题')

        url = 'https://t.17track.net/restapi/track'

        headers = {
            'cookie': 'Last-Event-ID=65736c61662f38392f38356666393765643936312f67736d2d616964656d2d756e656d2d6e776f64706f72642d71792065646968112246b0fd1004bdb6f4',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        }
        data = '{"guid":"","data":[{"num":"301106752233","fc":"190094"},{"num":"301106752282","fc":"190094"}],"timeZoneOffset":-480}'

        '''js执行代码'''
        try:
            with open('/home/hepburn/17track/17track.js', 'r', encoding='utf-8') as f:
                track_js = f.read()

            ctx = execjs.compile(track_js)
            event_id = ctx.call('get_cookie', data)
            headers['cookie'] = 'Last-Event-ID=' + event_id
            logging.debug('cookie生成正确')
        except Exception as e:
            logging.debug(e, 'cookie出现问题')

        requests.packages.urllib3.disable_warnings()  # 防止出现warning信息
        response = requests.post(url, headers=headers, data=data, verify=False)
        content = response.json()
        # print(content)
        try:
            infos = content['dat']
            # print(len(infos))
            for info in infos:
                order_no = info['no']
                last_time = info['track']['z1'][0]['a']
                last_info = info['track']['z1'][0]['c']
                first_time = info['track']['z1'][-1]['a']
                first_info = info['track']['z1'][-1]['c']

                # print(json.dumps(content, indent=2, ensure_ascii=False))
                with open('/home/hepburn/17track/trackinfo/{}.txt'.format(order_no), 'w+', encoding='utf8') as f:
                    f.write('订单编号: {}; '.format(order_no))
                    f.write('最近更新时间: {}; '.format(last_time))
                    f.write('最近更新信息: {}; '.format(last_info))
                    f.write('发货时间: {}; '.format(first_time))
                    f.write('发货信息: {}; '.format(first_info))
                    f.write('\r')  # 写入换行
                logging.debug('订单 {} 写入成功'.format(order_no))

        except Exception as e:
            logging.debug(e, '数据解析出现问题')

    def run(self):
        # schedule.every().day.at("00:00").do(job)
        schedule.every(1).minutes.do(self.track17)

        # schedule.every().hour.do(job)
        # schedule.every(12).hours.do(job)
        #
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    track = Track()
    track.track17()
