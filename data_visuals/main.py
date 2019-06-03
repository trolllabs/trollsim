from bokeh.io import curdoc
from bokeh.models.widgets import Tabs
from scripts.load_data import load_trollsim_log
from scripts.plot_log import MixedData


def main():
	path = 'bokeh-log/data/logdir'
	log_df = load_trollsim_log(path)
	print('Finished loading log.')
	print(log_df.describe())

	tab1 = MixedData(log_df).tab('All data')
	tabs = Tabs(tabs=[tab1])
	curdoc().add_root(tabs)


main()
