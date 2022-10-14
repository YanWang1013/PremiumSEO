import time
import subprocess


# ps -ef | grep cronjob
# kill -9 xxxx
def job():
    # subprocess.run('python3 01_retrieve_data.py', shell=True)
    # subprocess.run('python3 02_process_data.py', shell=True)
    # subprocess.run('python3 03_process_vocab_biz.py', shell=True)
    # subprocess.run('python3 04_process_vocab_loc.py', shell=True)
    # subprocess.run('python3 05_process_union_vocab.py', shell=True)
    # subprocess.run('python3 06_process_vocab_pre_biz.py', shell=True)
    # subprocess.run('python3 07_process_vocab_pre_loc.py', shell=True)
    # subprocess.run('python3 08_process_vocab_town.py', shell=True)
    # subprocess.run('sudo systemctl restart apache2', shell=True)
    # subprocess.run('sudo systemctl restart nginx', shell=True)
    # subprocess.run('sudo systemctl restart mlserver', shell=True)

    print('----------------- Started Cronjob -----------------------')
    subprocess.run('python 01_retrieve_data.py', shell=True)
    # subprocess.run('python3 01_retrieve_data.py', shell=True)
    subprocess.run('python 02_process_data.py', shell=True)
    # subprocess.run('python3 02_process_data.py', shell=True)
    subprocess.run('python 03_process_vocab_biz.py', shell=True)
    # subprocess.run('python3 03_process_vocab_biz.py', shell=True)
    subprocess.run('python 04_process_vocab_loc.py', shell=True)
    # subprocess.run('python3 04_process_vocab_loc.py', shell=True)
    subprocess.run('python 05_process_union_vocab.py', shell=True)
    # subprocess.run('python3 05_process_union_vocab.py', shell=True)
    subprocess.run('python 06_process_vocab_pre_biz.py', shell=True)
    # subprocess.run('python3 06_process_vocab_pre_biz.py', shell=True)
    subprocess.run('python 07_process_vocab_pre_loc.py', shell=True)
    # subprocess.run('python3 07_process_vocab_pre_loc.py', shell=True)
    subprocess.run('python 08_process_vocab_town.py', shell=True)
    # subprocess.run('python3 08_process_vocab_town.py', shell=True)
    print('------------------ Finished Cronjob -------------------------')


# schedule.every().day.at('07:40').do(job)

# while True:
#    schedule.run_pending()
#    time.sleep(1)
job()
