from copy import deepcopy

from md2book.config import *
from md2book.util.common import escapePath

class BaseModule:
	NAME = None # None for a module auto-loaded without configuration
	
	def __init__(self, conf, target):
		self.conf = conf
		self.target = target
		self.format = target.format

	def get_conf_name(self):
		return self.NAME

	def get_custom_css(self):
		return []

	def get_stylesheets(self):
		return []

	def get_scripts(self):
		return []

	def alter_target(self):
		pass

	def alter_html(self, code):
		pass

	def pandoc_options(self, dest_format):
		return []

	def alter_md(self, code):
		pass

# -------------------- MODULE FOR ALL BASE DATAS -------------------- #

class MainTargetDatasModule(BaseModule):
	"""
		This module does not behave like all other modules.
		It manage the BASE configuration
	"""
	def alter_target(self):
		conf = self.target.conf
		if conf.get('title', None) is None:
			conf['title'] = conf['name']
		if conf['theme']:
			self.target.theme_path = DATA_PATH / 'styles' / 'themes' / '{}.css'.format(conf['theme'])

		# Stylesheets
		conf_css = [(self.target.path.parent / p).resolve() for p in conf['css']]
		# conf_css = conf['css']

		base_styles = deepcopy(BASE_STYLES['default'])
		if conf['theme']:
			base_styles.append(self.target.theme_path)
		if self.format in BASE_STYLES:
			base_styles.extend(BASE_STYLES[self.format])

		self.target.stylesheets = base_styles + self.target.stylesheets + conf_css

		# Scripts
		for script in conf['js']:
			if script in AVAILABLE_SCRIPTS:
				script = AVAILABLE_SCRIPTS[script]
			self.target.scripts.append(script)

	def pandoc_options(self, dest_format):
		options = super().pandoc_options(dest_format)
		if dest_format == 'epub':
			for path in self.target.stylesheets:
				options.append("--css=" + escapePath(path))
		return options