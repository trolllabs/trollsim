import numpy as np
import scipy.signal as signal
from pandas import DataFrame, to_datetime
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Panel
from bokeh.models.widgets import CheckboxGroup, RadioButtonGroup, PreText, Paragraph


class ProcessedData:
	def __init__(self, logdata: DataFrame):
		self.logdata = logdata[logdata.Name == 'ECG LL-RA CAL (mVolts)']
		print(self.logdata.head(4).values)

		num_frequencies = 100000
		frequencies = np.linspace(0.01, 50, num_frequencies)
		periodogram = signal.lombscargle(self.logdata.Timestamp, self.logdata.Value, frequencies)
		self.plot_data = DataFrame(columns=['frequencies', 'power'])
		self.plot_data.frequencies = frequencies
		self.plot_data.power = periodogram

	def tab(self, name):
		fig = figure(
				title='Lomb Scargle Periodogram',
				plot_width=conf.PLOTWIDTH,
				plot_height=conf.PLOTHEIGHT,
				x_axis_label='Frequency',
				y_axis_label='Power'
				)

		fig.line('frequencies', 'power', source=self.plot_data, line_width=2)

		layout = column(Paragraph(text='Lomb Scargle Periodogram of LL-RA physio'), fig)
		return Panel(child=layout, title=name)

