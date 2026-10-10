"""One-time saved-workspace migration for the shared Tap action."""
from apply_native import replace

def apply():
    replace('mscore/workspace.cpp','static constexpr int WORKSPACE_UI_VERSION = 3;','static constexpr int WORKSPACE_UI_VERSION = 4;')
    replace('mscore/workspace.cpp','''                  mscore->populateAlternativeOperations();
                  }
            }
      }

//---------------------------------------------------------
//   readMenu''','''                  mscore->populateAlternativeOperations();
                  }
            }
      if (uiVersion < 4) {
            ensureMenuAction("menu-tools", "tap-tempo", "transpose");
            if (auto entries = mscore->playbackControlEntries()) {
                  ensureToolbarEntry(*entries, "tap-tempo", "independent-metronome", InsertPosition::AFTER);
                  mscore->populatePlaybackControls();
                  }
            }
      }

//---------------------------------------------------------
//   readMenu''')

if __name__=='__main__':apply()
