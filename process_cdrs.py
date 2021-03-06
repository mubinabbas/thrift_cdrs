import os
import sys
import csv
import glob
import shutil
import time
from datetime import datetime
from ftplib import FTP
import pytz.reference
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol



thrift_config = {
                'sm7': [('/var/cdrs/env1/', '/var/data/cdrs/env1', 8), ('/var/cdrs/env3', '/var/data/cdrs/env3', 13)],
                'sm8': [('/var/writable/','/var/data/cdrs/env1',9)],
                'sm9': [('/storage/cdrs/env1', '/var/data/cdrs/env1', 11)],
                'sm10': [('/var/thrift-cdrs/', '/var/data/cdrs/env1', 12)]
                }


sys.path.append('/var/data/thrift_cdrs/thrift_stub_dir')
from ssp import ttypes

valid_cdr_files = {
                    'cdrs_connections-thrift': [ttypes.CdrsConnections, []],
                    'cdrs_customers-thrift': [ttypes.CdrsCustomers, []],
                    'calls-thrift': [ttypes.Calls, []],
                    'cdrs-thrift': [ttypes.Cdrs, []],
                    'calls_sdp-thrift': [ttypes.CallsSdp, []]
                    }


valid_cdr_files['calls-thrift'][1] = ['i_call','call_id','cld','cli','setup_time','parent_i_call','i_call_type']

valid_cdr_files['cdrs-thrift'][1] = ['i_cdr','i_call','i_account','result','cost','delay','duration','billed_duration',
                                    'connect_time','disconnect_time','cld_in','cli_in','prefix','price_1','price_n',
                                    'interval_1','interval_n','post_call_surcharge','connect_fee','free_seconds',
                                    'remote_ip','grace_period','user_agent','pdd1xx','i_protocol','release_source',
                                    'plan_duration','accessibility_cost','lrn_cld','lrn_cld_in','area_name','p_asserted_id',
                                    'remote_party_id']

valid_cdr_files['cdrs_customers-thrift'][1] = ['i_cdrs_customer','i_cdr','i_customer','cost','billed_duration','prefix','price_1',
                                    'price_n','interval_1','interval_n','post_call_surcharge','connect_fee','free_seconds',
                                    'grace_period','i_call','i_wholesaler','setup_time','duration','area_name']

valid_cdr_files['cdrs_connections-thrift'][1] = ['i_cdrs_connection','i_call','i_connection','result','cost','delay','duration',
                                    'billed_duration','setup_time','connect_time','disconnect_time','cld_out','cli_out','prefix',
                                    'price_1','price_n','interval_1','interval_n','post_call_surcharge','connect_fee','free_seconds',
                                    'grace_period','user_agent','pdd100','pdd1xx','i_account_debug','i_protocol','release_source',
                                    'call_setup_time','lrn_cld','area_name','i_media_relay','remote_ip','vendor_name']

valid_cdr_files['calls_sdp-thrift'][1] = ['i_calls_sdp','i_call','i_cdrs_connection','time_stamp','sig_ip','rtp_ip','codec','sip_msg_type']

codecs = {'0': 'PCMU', '3': 'GSM', '4': 'G723', '8': 'PCMA', '9': 'G722', '15': 'G728', '18': 'G729'}



def align_struct(obj, i_switch):
    st = dict(obj.__dict__)
    if type(obj)==ttypes.Calls:
        st['i_call'] = '%d.%d' % (st['i_call'], i_switch)
        st['setup_time'] = datetime.fromtimestamp(obj.setup_time, pytz.reference.UTC).strftime('%Y-%m-%d %H:%M:%S+00:00')
        st['parent_i_call'] = obj.parent_i_call.v if obj.parent_i_call else None
        st['i_call_type'] = obj.i_call_type.v if obj.i_call_type else None
        return st
    elif type(obj)==ttypes.Cdrs:
        st['i_call'] = '%d.%d' % (st['i_call'], i_switch)
        st['i_cdr'] = '%d.%d' % (st['i_cdr'], i_switch)
        st['lrn_cld'] = obj.lrn_cld.s if obj.lrn_cld else None
        st['lrn_cld_in'] = obj.lrn_cld_in.s if obj.lrn_cld_in else None
        st['area_name'] = obj.area_name.s if obj.area_name else None
        st['p_asserted_id'] = obj.p_asserted_id.s if obj.p_asserted_id else None
        st['remote_party_id'] = obj.remote_party_id.s if obj.remote_party_id else None
        st['connect_time'] = datetime.fromtimestamp(obj.connect_time, pytz.reference.UTC).strftime('%Y-%m-%d %H:%M:%S+00:00')
        st['disconnect_time'] = datetime.fromtimestamp(obj.disconnect_time, pytz.reference.UTC).strftime('%Y-%m-%d %H:%M:%S+00:00')
        return st
    elif type(obj)==ttypes.CdrsConnections:
        st['i_call'] = '%d.%d' % (st['i_call'], i_switch)
        st['i_cdrs_connection'] = '%d.%d' % (st['i_cdrs_connection'], i_switch)
        st['setup_time'] = datetime.fromtimestamp(obj.setup_time, pytz.reference.UTC).strftime('%Y-%m-%d %H:%M:%S+00:00')
        st['connect_time'] = datetime.fromtimestamp(obj.connect_time, pytz.reference.UTC).strftime('%Y-%m-%d %H:%M:%S+00:00')
        st['disconnect_time'] = datetime.fromtimestamp(obj.disconnect_time, pytz.reference.UTC).strftime('%Y-%m-%d %H:%M:%S+00:00')
        st['call_setup_time'] = datetime.fromtimestamp(obj.call_setup_time, pytz.reference.UTC).strftime('%Y-%m-%d %H:%M:%S+00:00')
        st['lrn_cld'] = obj.lrn_cld.s if obj.lrn_cld else None
        st['area_name'] = obj.area_name.s if obj.area_name else None
        st['i_media_relay'] = obj.i_media_relay.v if obj.i_media_relay else None
        st['remote_ip'] = obj.remote_ip.s if obj.remote_ip else None
        st['vendor_name'] = obj.vendor_name.s if obj.vendor_name else None
        return st
    elif type(obj)==ttypes.CdrsCustomers:
        st['i_call'] = '%d.%d' % (st['i_call'], i_switch)
        st['i_cdrs_customer'] = '%d.%d' % (st['i_cdrs_customer'], i_switch)
        st['i_cdr'] = '%d.%d' % (st['i_cdr'], i_switch)
        st['setup_time'] = datetime.fromtimestamp(obj.setup_time, pytz.reference.UTC).strftime('%Y-%m-%d %H:%M:%S+00:00')
        st['area_name'] = obj.area_name.s if obj.area_name else None
        return st
    elif type(obj)==ttypes.CallsSdp:
        #st['i_call'] = '%d.%d' % (st['i_call'], i_switch)
        #st['i_calls_sdp'] = '%d.%d' % (st['i_calls_sdp'], i_switch)
        #st['i_cdrs_connection'] = '%d.%d' % (obj.i_cdrs_connection.v, i_switch) if obj.i_cdrs_connection!=None else '-1'
        st['i_cdrs_connection'] = obj.i_cdrs_connection.v if obj.i_cdrs_connection!=None else '-1'
        st['time_stamp'] = datetime.fromtimestamp(obj.time_stamp.seconds, pytz.reference.UTC).strftime('%Y-%m-%d %H:%M:%S+00:00')
        lsdp = compile_sdp(obj.sdp)
        st['sig_ip']=get_sigip(lsdp)
        st['rtp_ip']=get_rtpip(lsdp)
        st['codec']=get_codec(lsdp)
        return st

    return None


def compile_sdp(sdp):
    if not sdp:
        avpairs = []
    else:
        avpairs = [x.split('=', 1) for x in sdp.strip().splitlines() if len(x.strip()) > 0]

    avp=[]
    s=0
    for v, param in avpairs:
        if v.strip().lower() in ['c', 'm', 'a', 'o']:
            if v.strip().lower()=='m':
                if s > 0:
                    break
                s=1

            avp.append([v.strip().lower(), param.strip()])

    return avp

def get_sigip(avpairs):
    for v, param in avpairs:
        if v == 'o' and len(param.split())==6:
            return param.split()[-1].strip()

    return ''


def get_rtpip(avpairs):
    for v, param in avpairs:
        if v == 'c' and len(param.split())==3:
            return param.split()[-1].strip()

    return ''



def get_codec(avpairs):
    cd=''
    for v, param in avpairs:
        if v == 'm' and len(param.split())>3 and param.split()[0].strip().lower()=='audio':
            cd = param.split()[3].strip()
            break

    if cd not in codecs:
        return ''

    annexb=''
    for v, param in avpairs:
        if v == 'a' and param.lower().startswith('fmtp:'+cd) and len(param.split())>1:
            ab = param.split()[1].split('=')
            if len(ab)==2 and ab[1].strip().lower()!='no':
                annexb='(B)'

    return codecs[cd]+annexb


def get_bdb_connection(env):
    sys.path.append('/var/data/thrift_cdrs')
    import bsddb185

    bdb = bsddb185.hashopen(os.path.join(env, 'copiedfiles.db'), 'c')
    return bdb


def pull_cdrs(switchname):
    for env in thrift_config[switchname]:
        try:
            os.makedirs(env[1])
        except:
            pass

        bdb = get_bdb_connection(env[1])
        for cdr_file in glob.glob(os.path.join(env[0],'*sdp*.bin.*')):
            try:
                filename = cdr_file.split('/')[-1]
                tag = filename.split('.')[0]
            except:
                tag = ''
                filename = ''

            if tag not in valid_cdr_files:
                continue

            if bdb.has_key(filename):
                continue

            bdb[filename]='OK'
            shutil.copy(cdr_file, env[1])
            print cdr_file

        bdb.sync()
        bdb.close()


def upload_csv(switchname):
    ftp = FTP('170.178.202.138')
    ftp.login("bhaoo-cdrs", '{bits14Operator!New}')
    ftp.cwd('sippy')
    for csv_file in glob.glob('/var/data/cdrs/*sdp*.bin.*.csv'):
        try:
            file_dst = csv_file.split('/')[-1]
            file = open(csv_file, 'rb')
            ftp.storbinary('STOR ' + file_dst + '.tmp', file)
            file.close()
            ftp.rename(file_dst + '.tmp', file_dst)
            os.remove(csv_file)
        except:
            print "Error while uploading files...\n"

    ftp.quit()
    return


def make_csv(switchname):
    for env in thrift_config[switchname]:
        i_switch = env[2]
        for cdr_file in glob.glob(os.path.join(env[1],'*sdp*.bin.*')):
            try:
                filename = cdr_file.split('/')[-1]
                tag = filename.split('.')[0]
            except:
                tag = ''
                filename = ''

            if tag not in valid_cdr_files:
                continue

            print cdr_file
            csv_name = '%s_%d_%s.csv' % (switchname, i_switch, filename)
            csvfile = open(os.path.join('/var/data/cdrs', csv_name), "wb")
            wr = csv.DictWriter(csvfile, delimiter='`', escapechar='\\', lineterminator='\n', quoting=csv.QUOTE_NONE, fieldnames=valid_cdr_files[tag][1], extrasaction='ignore')

            fd = file(cdr_file)
            t = TTransport.TFileObjectTransport(fd)
            p = TBinaryProtocol.TBinaryProtocolAccelerated(t)
            while True:
                obj = valid_cdr_files[tag][0]()
                try:
                    obj.read(p)
                    wr.writerow(align_struct(obj, i_switch))
                except EOFError:
                    break

            csvfile.close()
            os.remove(cdr_file)

if __name__ == "__main__":
    try:
        if len(sys.argv) < 1:
            print "Wrong number of arguments"
            exit()
    except Exception, m:
        print m

    switchname = sys.argv[1]
    if switchname not in thrift_config:
        print '%s undefined switch' % switchname
        exit()

    pull_cdrs(switchname)
    make_csv(switchname)
    upload_csv(switchname)

