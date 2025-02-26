import contextvars


current_ontology = contextvars.ContextVar("current_ontology")
current_graph = contextvars.ContextVar("current_graph", default=None)
