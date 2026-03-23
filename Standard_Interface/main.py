from Forge.Standard_Interface.Presenter import datapresenter
from Forge.Standard_Interface.Model import datamodel
from Forge.Standard_Interface.View import dataview

view = dataview.DataView()
model = datamodel.DataModel()
presenter = datapresenter.DataPresenter(model = model, view = view)
view.setup(presenter)
view.start()





