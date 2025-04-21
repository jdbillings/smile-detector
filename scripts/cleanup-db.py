if __name__ == "__main__":
    import os
    import json
    import shutil
    
    script_dir = os.path.dirname(__file__)
    config_path = f"{script_dir}/../python/conf/config.json"

    with open(config_path , "r") as f:
        dbpath = json.load(f)["sqlite"]["db_path"]
        try:
            shutil.rmtree(dbpath)
        except FileNotFoundError:
            pass