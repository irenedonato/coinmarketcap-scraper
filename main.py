import argparse
from scraper import Scraper

def main():
    """
    serves the class Scraper as a command line interface
    """
    parser = argparse.ArgumentParser(description='scrape ')
        
    parser.add_argument('geckodriver_path', 
                        metavar='geckodriver',
                        type=str,
                        help='path to geckodriver executable file')
                        
    parser.add_argument('--load_time',
                        '-load_time',
                        type=int,
                        nargs='?', default=2,
                        help='waiting time to load the page')

    parser.add_argument('--out_dir',
                        '-out_dir',
                        type=str,
                        nargs='?', default='coin_data',
                        help='the path to list')

    parser.add_argument('--months',
                        '-months',
                        type=int,
                        nargs='?', default=38,
                        help='months of data to collect')
        
    parser.add_argument('--reload',
                        '-reload',
                        type=bool,
                        nargs='?', default=False,
                        help='refresh crypto already in out_dir')

    parser.add_argument('--coin','-coin',
                        type=str, nargs='+',
                        help='specific coin to load')

    args = parser.parse_args()

            
    s = Scraper(args.load_time, args.geckodriver_path, args.out_dir, args.months)
    if args.coin:
        for c in args.coin:
            s.get_currencies(c)
    else:
        s.get_currencies()
    
if __name__ == '__main__':
    main()    