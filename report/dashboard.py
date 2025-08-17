from fasthtml.common import *
import matplotlib.pyplot as plt

# Import QueryBase, Employee, Team from employee_events
from employee_events.query_base import QueryBase
from employee_events.employee import Employee
from employee_events.team import Team

# import the load_model function from the utils.py file
from utils import load_model

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
    )

from combined_components import FormGroup, CombinedComponent


# Create a subclass of base_components/dropdown
# called `ReportDropdown`
class ReportDropdown(Dropdown):
    
    # Overwrite the build_component method
    # ensuring it has the same parameters
    # as the Report parent class's method
    def build_component(self, entity_id, model):
        #  Set the `label` attribute so it is set
        #  to the `name` attribute for the model
        self.label = model.name.capitalize() if hasattr(model, "name") else "Select"
        # Delegamos al padre (sin kwargs)
        return super().build_component(entity_id, model)
    
    # Overwrite the `component_data` method
    # Ensure the method uses the same parameters
    # as the parent class method
    def component_data(self, entity_id, model):
        # Employee.names() -> [(full_name, employee_id)]
        # Team.names()     -> [(team_name, team_id)]
        # El Dropdown de tu plantilla espera (label, value),
        # así que NO invertimos: devolvemos tal cual.
        pairs = model.names()
        return pairs


# Create a subclass of base_components/BaseComponent
# called `Header`
class Header(BaseComponent):

    def build_component(self, entity_id, model):
        title = f"Desempeño del {model.name}" if hasattr(model, "name") else "Dashboard"
        return H1(title.capitalize())
          

# Create a subclass of base_components/MatplotlibViz
# called `LineChart`
class LineChart(MatplotlibViz):
    
    def visualization(self, entity_id, model):
        df = model.event_counts(entity_id)
        if df is None or df.empty:
            fig, ax = plt.subplots()
            ax.set_title("No hay datos")
            return fig
        
        df = df.fillna(0)
        df = df.set_index("event_date")
        df = df.sort_index()
        cum = df[["positive_events", "negative_events"]].cumsum()
        cum.columns = ["Positive", "Negative"]
        fig, ax = plt.subplots()
        cum.plot(ax=ax)
        # Estilo de ejes (llamada segura, por compatibilidad)
        try:
            self.set_axis_styling(ax, border_color="black", font_color="black")
        except TypeError:
            try:
                self.set_axis_styling(ax, border="black", font="black")
            except TypeError:
                self.set_axis_styling(ax)
        ax.set_title("Eventos acumulados", fontsize=16)
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Conteo")
        return fig


# Create a subclass of base_components/MatplotlibViz
# called `BarChart`
class BarChart(MatplotlibViz):

    predictor = load_model()

    def visualization(self, entity_id, model):
        X = model.model_data(entity_id)
        if hasattr(self.predictor, "predict_proba"):
            proba = self.predictor.predict_proba(X)
        else:
            pred = self.predictor.predict(X)
            import numpy as np
            proba = np.array([[max(0.0, min(1.0, float(pred[0])))]])

        import numpy as np
        if not isinstance(proba, np.ndarray):
            proba = np.array(proba)
        if proba.ndim == 2 and proba.shape[1] > 1:
            pos = proba[:, 1:2]
        else:
            pos = proba[:, :1]
        
        if getattr(model, "name", "") == "team":
            pred = float(pos.mean())
        else:
            pred = float(pos[0, 0])
        
        fig, ax = plt.subplots()
        ax.barh([""], [pred])
        ax.set_xlim(0, 1)
        ax.set_title("Predicted Recruitment Risk", fontsize=20)
        # Estilo de ejes (llamada segura)
        try:
            self.set_axis_styling(ax, border_color="black", font_color="black")
        except TypeError:
            try:
                self.set_axis_styling(ax, border="black", font="black")
            except TypeError:
                self.set_axis_styling(ax)
        return fig
 
# Create a subclass of combined_components/CombinedComponent
# called Visualizations       
class Visualizations(CombinedComponent):
    children = [LineChart(), BarChart()]
    outer_div_type = Div(cls="grid")
            
# Create a subclass of base_components/DataTable
# called `NotesTable`
class NotesTable(DataTable):

    def component_data(self, entity_id, model):
        return model.notes(entity_id)
    

class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name="profile_type",
            hx_get="/update_dropdown",
            hx_target="#selector"
            ),
        ReportDropdown(
            id="selector",
            name="user-selection")
        ]
    
# Create a subclass of CombinedComponents
# called `Report`
class Report(CombinedComponent):
    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]

# Initialize a fasthtml app 
app, rt = fast_app()

# Initialize the `Report` class
report = Report()

# -------- Helpers para convertir nombre -> id si fuera necesario --------
def _resolve_employee_id(id_or_name: str) -> int:
    try:
        return int(id_or_name)
    except Exception:
        for name, eid in Employee().names():
            if name == id_or_name:
                return int(eid)
    # fallback seguro
    return 1

def _resolve_team_id(id_or_name: str) -> int:
    try:
        return int(id_or_name)
    except Exception:
        for name, tid in Team().names():
            if name == id_or_name:
                return int(tid)
    return 1


# Create a route for a get request
# Set the route's path to the root
@app.get("/")
def home():
    return report(1, Employee())

# employee page
@app.get("/employee/{id:str}")
def employee(id: str):
    emp_id = _resolve_employee_id(id)
    return report(emp_id, Employee())

# team page
@app.get("/team/{id:str}")
def team(id: str):
    team_id = _resolve_team_id(id)
    return report(team_id, Team())


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id_val = data._dict['user-selection']
    if profile_type == 'Employee':
        # si por algún motivo llega nombre, lo resolvemos
        return RedirectResponse(f"/employee/{_resolve_employee_id(id_val)}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{_resolve_team_id(id_val)}", status_code=303)
    

serve()
