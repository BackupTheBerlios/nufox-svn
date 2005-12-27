from nufox import deploy

from examples import _base


application = deploy.NufoxServer(
    'NufoxExamples', 8080, _base.NufoxExamples, interface='127.0.0.1')
