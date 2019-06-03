import scripts.config as conf
from bokeh.palettes import Category20_16
from bokeh.layouts import column, row, WidgetBox
from bokeh.models.widgets import CheckboxGroup, PreText
from bokeh.models import ColumnDataSource, Panel, Span, HoverTool, CDSView, GroupFilter
from bokeh.plotting import figure
from pandas import DataFrame, to_datetime


class MixedData:
	def __init__(self, logdata: DataFrame):
		self.line_dataset = None
		self.scatter_dataset = None
		self.logdata = logdata

		# Partition markers
		self.span_locations = logdata[logdata.Name.isin(conf.sections)]
		self.logdata = self.logdata[~self.logdata.Name.isin(conf.sections)]
		self.logdata.Timestamp = to_datetime(self.logdata.Timestamp, unit='ms')

		# Scatter data
		self.scatter_data = self.logdata

		# Multi line data prep
		self.line_data = self.logdata.groupby('Channel').aggregate({'Timestamp': list, 'Value': list})

		self.id_list = list(self.line_data.index)
		self.id_list.sort()
		self.line_channel_checkbox = CheckboxGroup(labels=self.id_list)
		self.line_channel_checkbox.on_change('active', self.lineplot_handler)
		self.scatter_channel_checkbox = CheckboxGroup(labels=self.id_list)
		self.scatter_channel_checkbox.on_change('active', self.scatterplot_handler)

	def generate_scatter_dataset(self, log_data, active_channels):
		visible_data = DataFrame(columns=['Timestamp', 'Value', 'Channel', 'color'])

		for i, channel in enumerate(active_channels):
			visible_channel = log_data[log_data['Channel'] == channel]
			visible_channel['color'] = conf.SCATTER_COLOR[i]
			visible_data = visible_data.append(visible_channel, sort=True)

		return ColumnDataSource(visible_data)

	def generate_line_dataset(self, log_data, active_channels):
		visible_data = DataFrame(columns=['Timestamp', 'Value', 'Channel', 'color'])

		for i, channel in enumerate(active_channels):
			visible_channel = log_data.loc[channel]
			visible_channel['color'] = conf.LINE_COLOR[i]
			visible_channel['Channel'] = channel
			visible_data = visible_data.append(visible_channel, sort=True)

		return ColumnDataSource(visible_data)

	def generate_figure(self, line_data: ColumnDataSource, scatter_data: ColumnDataSource):
		fig = figure(
				title='Log',
				plot_width=conf.PLOTWIDTH,
				plot_height=conf.PLOTHEIGHT,
				x_axis_label='Timestamp (ms)',
				y_axis_label='Value'
				)

		fig.multi_line('Timestamp', 'Value', source=line_data, line_width=2, color='color', legend='Channel')
		fig.scatter('Timestamp', 'Value', source=scatter_data, legend='Channel', marker='circle', color='color')
		return fig

	def scatterplot_handler(self, attr, old, new):
		active_channels = [self.scatter_channel_checkbox.labels[i] for i in new]
		new_dataset = self.generate_scatter_dataset(self.scatter_data, active_channels)
		self.scatter_dataset.data.update(new_dataset.data)

	def lineplot_handler(self, attr, old, new):
		active_channels = [self.line_channel_checkbox.labels[i] for i in new]
		new_dataset = self.generate_line_dataset(self.line_data, active_channels)
		self.line_dataset.data.update(new_dataset.data)

	def tab(self, name):
		initial_line_channels = [self.line_channel_checkbox.labels[i] for i in self.line_channel_checkbox.active]
		self.line_dataset = self.generate_line_dataset(self.line_data, initial_line_channels)

		initial_scatter_channels = [self.scatter_channel_checkbox.labels[i] for i in self.scatter_channel_checkbox.active]
		self.scatter_dataset = self.generate_scatter_dataset(self.scatter_data, initial_scatter_channels)

		fig = self.generate_figure(self.line_dataset, self.scatter_dataset)

		# For sectioning the figure
		for span_location in self.span_locations.itertuples():
			span = Span(
					location=span_location.Timestamp,
					dimension='height',
					line_color='red',
					line_dash='dashed',
					line_width=2
					)
			fig.add_layout(span)

			# Add hovertool trick
			hovertool_cheat = fig.line(
					[span_location.Timestamp, span_location.Timestamp],
					[-10, 10],
					line_width=0,
					line_color='red',
					line_dash='dashed'
					)
			hovertool = HoverTool(
					renderers=[hovertool_cheat],
					tooltips=[
						(span_location.Name, str(span_location.Timestamp))
						]
					)
			fig.add_tools(hovertool)

		lineplot_text = PreText(text='Lineplot channels')
		scatterplot_text = PreText(text='Scatterplot channels')

		#layout = row(self.line_channel_checkbox, fig)
		layout = row(
				column(
					lineplot_text,
					self.line_channel_checkbox,
					scatterplot_text,
					self.scatter_channel_checkbox
					),
				fig
				)
		return Panel(child=layout, title=name)

