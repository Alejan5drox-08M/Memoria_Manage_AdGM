# -*- coding: utf-8 -*-
from email.policy import default

from odoo import models, fields, api
import datetime

class manage(models.Model):
     _name = 'manage.manage'
     _description = 'manage.manage'

class task(models.Model):
    _name='manage.task'
    _description='manage.task'

    name = fields.Char(string="Nombre", readonly=False, required=True, help="Introduzca el nombre")
    description = fields.Text(string="Descripción")
    start_date = fields.Datetime(string="Fecha de inicio")
    end_date = fields.Datetime(string="Fecha de fin")
    is_paused = fields.Boolean(string="¿Pausado?")
    sprint_id = fields.Many2one("manage.sprint", string="Sprint", ondelete="cascade",compute="_get_sprint", store=True)
    history_id = fields.Many2one("manage.history", string="History", required=True, ondelete="cascade")
    technology_id = fields.Many2many(comodel_name="manage.technology",
                                   relation="technogies_tasks",
                                   column1="technologies_ids",
                                   column2="tasks_ids")
    definition_date = fields.Datetime(default=lambda p:datetime.datetime.now())
    project = fields.Many2one("manage.project", related="history_id.project_id", readonly=True)
    code = fields.Char(compute="_get_code")

class sprint(models.Model):
    _name='manage.sprint'
    _description='manage.sprint'
    code = fields.Char(string="Codigo", compute="_get_code")
    name = fields.Char(string="Nombre", readonly=False, required=True, help="Introduzca el nombre")
    description = fields.Text(string="Descripción")
    start_date = fields.Datetime(string="Fecha de inicio")
    end_date = fields.Datetime(string="Fecha de fin", compute="_get_end_date", store=True)
    duration = fields.Integer(string="Duracion",default="15")
    task_id = fields.One2many(string="Tasks", comodel_name="manage.task", inverse_name="sprint_id")
    project_id = fields.Many2one("manage.project", string="Project", required=True, ondelete="cascade")

    def _get_code(self):
        for sprint in self:
            if len(sprint.task_id) == 0:
                sprint.code = "FILM_"+str(sprint.id)
            else:
                sprint.code = str(sprint.task_id.name).upper()+"_"+str(sprint.id)

    @api.depends('start_date','duration')
    def _get_end_date(self):
        for sprint in self:
            if isinstance(sprint.start_date,datetime.datetime) and sprint.duration>0:
                sprint.end_date=sprint.start_date+datetime.timedelta(days=sprint.duration)
            else:
                sprint.end_date=sprint.start_date

    @api.depends('code')
    def _get_sprint(self):
        #global sprints, task, found
        for task in self:
            sprints = self.env['manage.sprint'].search([('project.id', '=', task.history.project.id)])
            found = False
        for sprint in sprints:
            if isinstance(sprint.end_date, datetime.datetime) and sprint.end_date > datetime.datetime.now():
                task.sprint = sprint.id
                found = True
        if not found:
            task.sprint = False



class project(models.Model):
    _name='manage.project'
    _description='manage.project'

    name = fields.Char(string="Nombre", readonly=False, required=True, help="Introduzca el nombre")
    description = fields.Text(string="Descripción")
    history_id = fields.One2many(string="Histories", comodel_name="manage.history", inverse_name="project_id")
    sprint_id = fields.One2many(string="Sprints", comodel_name="manage.sprint", inverse_name="project_id")

class history(models.Model):
    _name='manage.history'
    _description='manage.history'

    name = fields.Char(string="Nombre", readonly=False, required=True, help="Introduzca el nombre")
    description = fields.Text(string="Descripción")
    task_id = fields.One2many(string="Tasks", comodel_name="manage.task", inverse_name="history_id")
    project_id = fields.Many2one("manage.project", string="Project", required=True, ondelete="cascade")
    used_technologies = fields.Many2many("manage.technology", compute="_get_used_technologies")

    def _get_used_technologies(self):
        for history in self:
            technologies = None  # Array para concatenar todas las tecnologias. Inicialmente no tiene valor
            for task in history.task_id:  # Para cada una de las tareas de la historia
                if not technologies:
                    technologies = task.technology_id
                else:
                    technologies = technologies + task.technology_id
            history.used_technologies = technologies # Asignar las tecnologias a la historia

class technology(models.Model):
    _name='manage.technology'
    _description='manage.technology'

    name = fields.Char(string="Nombre", readonly=False, required=True, help="Introduzca el nombre")
    description = fields.Text(string="Descripción")
    photo = fields.Image(string="Imagen")
    tasks_id = fields.Many2many(comodel_name="manage.task",
                                    relation="technologies_tasks",
                                    column1="tasks_ids",
                                    column2="technologies_ids")

class developer(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    is_dev = fields.Boolean()
    technologies = fields.Many2many("manage.technology",
              relation="developer_technologies",
              column1="developer_id",
              column2="technologies_id")