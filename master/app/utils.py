import trafaret as t
import yaml

CONFIG_TRAFARET = t.Dict(
    {
        t.Key('secondaries'): t.List(t.Dict({
            'url': t.String(),
            'name': t.String(),
        })
        ),
        'host': t.IP,
        'port': t.Int(),
    }
)


def load_config(fname):
    with open(fname, 'rt') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return CONFIG_TRAFARET.check(data)
