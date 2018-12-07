from frappe import _

def get_data():
	return {
		'heatmap': True,
		'fieldname': 'appartment',
		'transactions': [
			{
				'label': _('Bookings'),
				'items': ['Booking']
			}
		]
	}