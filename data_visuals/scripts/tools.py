import scripts.shortcuts as shortcut
import pandas as pd


class SectionDescriptor:
	def __init__(self, start, end=None, duration=None):
		self.start = start
		self.end = end
		self.duration = duration

	def __str__(self):
		return 'Start: %s, End: %s, Duration: %s' % (self.start, self.end, self.duration)


def generate_sections(logdata: pd.DataFrame):
	"""
	Generates a list of SectionDescriptors based on iMotions packets
	SlideStart and SlideEnd.

	If the first Slide related packet is an End packet, the first
	descriptor will include all timestamps up to that packet, else it
	will drop the packets before.

	The last descriptor will include all packets until end.

	Assumes that there are SlideStart and SlideEnd packages in data.
	"""
	slide_start = logdata.Name == 'SlideStart'
	slide_end = logdata.Name == 'SlideEnd'
	slides = slide_start | slide_end

	log_slides = logdata[slides]
	time_diffs = log_slides.Timestamp.diff()

	sections = []
	if log_slides.iloc[0].Name == 'SlideStart':
		# Bootstrap condition
		sections.append(SectionDescriptor(shortcut.row_index(log_slides.head(1))))

	for label, timediff in time_diffs.iteritems():
		if not sections:
			# If first packet is a SlideEnd, we include all data before
			sections.append(SectionDescriptor(0, label, logdata.loc[label].Timestamp))
		elif not sections[-1].end:
			sections[-1].end = label
			sections[-1].duration = timediff
		else:
			sections.append(SectionDescriptor(label))

	last_row = logdata.tail(1).Timestamp
	last_label = shortcut.row_index(last_row)
	last_timestamp = last_row.values[0]
	sections[-1].end = last_label
	sections[-1].duration = logdata.loc[last_label].Timestamp - logdata.loc[sections[-1].start].Timestamp

	return sections

