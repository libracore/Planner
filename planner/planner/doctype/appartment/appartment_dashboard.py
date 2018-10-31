from frappe import _

def get_data():
	return {
		'heatmap': True,
		'fieldname': 'apartment',
		'transactions': [
			{
				'label': _('Connections'),
				'items': ['Customer', 'Sales Invoice', 'Sales Order']
			}
		]
	}