import invoke

import installers
import shims


namespace = invoke.Collection(installers, shims)
