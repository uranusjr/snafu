import invoke

import docs
import installers
import shims

namespace = invoke.Collection(docs, installers, shims)
