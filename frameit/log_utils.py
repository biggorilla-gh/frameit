import tqdm

def in_ipynb():
    try:
        cfg = get_ipython().config
        if cfg['IPKernelApp']['parent_appname'] == 'ipython-notebook':
            return True
        else:
            return False
    except NameError:
        return False

def log_progress(input_):
    if in_ipynb():
        return(tqdm.tqdm_notebook(input_))
    else:
        return(tqdm.tqdm(input_))