from libs.helper import *
from biz.send_email import *
from biz.deal_wx_concat import *
import time
class SendConcat:
    def __init__(self):
        self.db_helper = DBHelper()
        self.default_config = ConfigHelper.getDefault()
        self.cursor = None
        self.dealWxConcat = DealWxConcat()
        self.sendMail = SendMail()


    def execute_to(self):
        now = time.strftime("%Y-%m-%d", time.localtime())
        outPath = self.default_config['toexcel']['wx_concat_path']
        outName = outPath + "/" + now + "wx_concat.csv"
        outfile = "'"+outName+"'"
        sql ="SELECT b.id,external_name,ELT(gender,'男','女'),wc.inner_user_id, FROM_UNIXTIME(wc.created_time) into outfile "+outfile+" character set gbk fields terminated by ',' optionally enclosed by '\"' lines terminated by '\n'  FROM wechat_customer AS wc INNER JOIN contact_qrcode AS b ON wc.code_id = b.remark  where wc.created_time>=UNIX_TIMESTAMP(CAST(SYSDATE()AS DATE) - INTERVAL 1 DAY) ORDER BY wc.id desc"
        try:
            conn = self.db_helper.getConnect()
            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
            self.cursor = cursor
            cursor.execute(sql)
            cursor.close()
            time.sleep(10)
            re_file_name = self.dealWxConcat.execute_to(outName)
            subject = now+'拓展扫码'
            content_text = '推广员，昵称，性别，客服号，添加时间'
            receivers = []
            cc = []
            
        except pymysql.Error as e:
            error = 'MySQL execute failed! ERROR (%s): %s' % (e.args[0], e.args[1])
            subject = '发送扫码邮件失败!error'
            content_text = now + error
            receivers = []
            cc = []
     
        except Exception as e:
            error = 'ERROR (%s): %s' % (e.args[0], e.args[1])
            subject = '发送扫码邮件失败!error'
            content_text = now + error
            syn_logger.exception(e)
            cc = []
            receivers = []
   
        attachments = [re_file_name]
        self.sendMail.send_email_to(subject, content_text, attachments, receivers, cc)
