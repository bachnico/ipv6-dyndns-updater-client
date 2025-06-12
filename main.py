import yaml
import importlib
import time
import logging
import argparse
import threading

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def load_config(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def import_class(module_path, class_name):
    module = importlib.import_module(module_path)
    return getattr(module, class_name)

def run_job(job_conf, daemon=True):
    # Initialize Parser
    parser_conf = job_conf["parser"]
    ParserClass = import_class(f"parsers.{parser_conf['type']}", parser_conf['type'])
    parser = ParserClass(job_conf["parser"])

    # Initialize Updaters
    updaters = []
    for updater_conf in job_conf["updaters"]:
        UpdaterClass = import_class(f"updaters.{updater_conf['type']}", updater_conf['type'])
        updaters.append(UpdaterClass(updater_conf))

    def do_update():
        try:
            ips, sleep_time = parser.get_ips()
        except Exception as e:
            logging.error(f"[{job_conf['name']}] Parser failed: {e}")
            raise e
        
        for updater in updaters:
            try:
                ips_changed = updater.update(ips)
                if ips_changed:
                    logging.info(f"[{job_conf['name']}] Updater {updater.__class__.__name__} updated successfully.")
                else:
                    logging.info(f"[{job_conf['name']}] Updater {updater.__class__.__name__} executed successfully, but did not change IPs.")
                return sleep_time
                
            except Exception as e:
                logging.error(f"[{job_conf['name']}] Updater {updater.__class__.__name__} failed: {e}")
                raise e

    if not daemon:
        do_update()
    else:
        while True:
            sleep_time = do_update()
            logging.info(f"[{job_conf['name']}] Sleeping for {sleep_time} seconds before next update.")
            time.sleep(sleep_time)

def main():
    parser = argparse.ArgumentParser(description="IPv6 Updater")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--daemon", action="store_true", help="Run as a daemon (loop forever)")
    args = parser.parse_args()

    config = load_config(args.config)
    jobs = config.get("jobs", [])

    if len(jobs) == 0:
        logging.error("No jobs found in the configuration file.")
        return
    if len(jobs) == 1:
        run_job(jobs[0], daemon=args.daemon)
    else:
        threads = []
        for job_conf in jobs:
            t = threading.Thread(target=run_job, args=(job_conf, args.daemon), daemon=True)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

if __name__ == "__main__":
    main()
