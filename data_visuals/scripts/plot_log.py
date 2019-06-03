import scripts.config as conf
from bokeh.palettes import Category20_16
from bokeh.layouts import column, row, WidgetBox
from bokeh.models.widgets import CheckboxGroup
from bokeh.models import ColumnDataSource, Panel, Span, HoverTool, CDSView, GroupFilter
from bokeh.plotting import figure
from pandas import DataFrame, to_datetime


class MixedData:
	def __init__(self, logdata: DataFrame):
		self.dataset = None
		self.logdata = logdata
		self.logdata.Timestamp = to_datetime(self.logdata.Timestamp, unit='ms')

		# Partition markers
		self.span_locations = logdata[logdata.Name.isin(conf.sections)]
		self.logdata = self.logdata[~self.logdata.Name.isin(conf.sections)]

		# For plotting lines separately
		#self.views = []

		self.id_list = list(set(self.logdata['Channel']))
		self.id_list.sort()
		self.channel_checkbox = CheckboxGroup(labels=self.id_list)
		self.channel_checkbox.on_change('active', self.lineplot_handler)
		self.scatter_channel_checkbox = CheckboxGroup(labels=self.id_list)
		#self.scatter_channel_checkbox.on_change('active', self.update_

	def generate_dataset(self, log_data, active_channels):
		visible_data = DataFrame(columns=['Timestamp', 'Value', 'channel', 'color'])

		for i, channel in enumerate(active_channels):
			visible_channel = log_data[log_data['Channel'] == channel]
			visible_channel.color = Category20_16[i]
			visible_data = visible_data.append(visible_channel, sort=True)

		return ColumnDataSource(visible_data)

	def generate_figure(self, data: ColumnDataSource):
		fig = figure(
				title='Log',
				plot_width=conf.PLOTWIDTH,
				plot_height=conf.PLOTHEIGHT,
				x_axis_label='Timestamp (ms)',
				y_axis_label='Value'
				)

		#print(self.id_list)
		#v = CDSView(source=
		#fig.line('Timestamp', 'Value', source=data, line_width=2)
		fig.scatter('Timestamp', 'Value', source=data, legend='Name', marker='circle', color='color')
		#for view in self.views:
		#	fig.line('Timestamp', 'Value', source=data, legend='Name', view=view)
		#fig.line('Timestamp', 'Value', source=data, legend='Name')

		return fig

	def update(self, active_channels):
		new_dataset = self.generate_dataset(self.logdata, active_channels)
		self.dataset.data.update(new_dataset.data)

	def scatterplot_handler(self, attr, old, new):
		active_channels = [self.scatter_channel_checkbox.labels[i] for i in new]
		self.update(active_channels)

	def lineplot_handler(self, attr, old, new):
		active_channels = [self.channel_checkbox.labels[i] for i in new]
		self.update(active_channels)

	def tab(self, name):
		initial_channels = [self.channel_checkbox.labels[i] for i in self.channel_checkbox.active]
		self.dataset = self.generate_dataset(self.logdata, initial_channels)

		# Create channels
		#for channel in self.id_list:
		#	self.views.append(
		#			CDSView(source=self.dataset, filters=[
		#				GroupFilter(column_name='Channel name', group=channel)
		#				])
		#			)

		fig = self.generate_figure(self.dataset)

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

		layout = row(self.channel_checkbox, fig)
		return Panel(child=layout, title=name)

