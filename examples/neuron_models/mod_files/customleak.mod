TITLE Simple passive leak channel

COMMENT
A minimal NMODL mechanism: a passive leak current i = g * (v - e).

When this directory is zipped and registered as a ModEnvironment, the server
parses the NEURON block below and exposes a mechanism named "customleak" (the
SUFFIX) with the RANGE parameters g and e. A cell's compartment can then list
"customleak" among its mechanisms, exactly like a built-in such as "hh".
ENDCOMMENT

NEURON {
    SUFFIX customleak
    NONSPECIFIC_CURRENT i
    RANGE g, e
}

PARAMETER {
    g = 0.001 (S/cm2)
    e = -65 (mV)
}

ASSIGNED {
    v (mV)
    i (mA/cm2)
}

BREAKPOINT {
    i = g * (v - e)
}
