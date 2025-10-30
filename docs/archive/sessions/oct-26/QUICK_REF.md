# SEMV Python - Quick Reference (30-Second Context)

🎯 **Current Focus**: Python rewrite of SEMV (Semantic Version Manager)

📊 **Project Status**:
- ✅ Planning & Architecture (docs/ref/ organized)
- 🔴 **Development Phase** - Core module implementation
- ⬆️ Integration & Testing phases

🚨 **Critical Context**:
- **Blockers**: None currently identified
- **MVP**: Core modules (version parsing, git ops, project detection)
- **Current Sprint**: Architecture design and initial implementation

📋 **Current Tasks** (see docs/procs/SPRINT.md):
1. Design modular Python architecture
2. Implement core version parsing module
3. Create project detection system
4. Set up testing framework

🏗️ **Architecture**:
- **Branch**: admin/meta-process (Meta Process v2 implementation)
- **Key Commands**: `./bin/validate-docs.sh`, `pytest` (when ready)
- **Target**: 800-1,200 lines Python (70% reduction from 4,000-line Bash)

⚡ **Immediate Next Steps**:
1. Read docs/procs/CONTINUE.md for latest session status
2. Check docs/procs/SPRINT.md for prioritized tasks
3. Review docs/ref/semv_concepts.md for architecture patterns

🚨 **Critical Rules**:
- **ALWAYS** update CONTINUE.md at session end
- Follow modular architecture patterns from semv_concepts.md
- Maintain 100% functional compatibility with Bash SEMV
- Test thoroughly - performance target is 10x improvement
- **Never** commit without validation when tests available

📦 **Integration Context**:
- **Boxy**: Workflow system integration required
- **GitSim**: Git simulation tool integration
- **Languages**: Rust, JavaScript, Python, Bash support
- **Out of Scope**: Java, C/C++, Go language support

🔍 **Reference**: `~/repos/code/shell/bashfx/fx-semv` (original Bash implementation)
📖 **Documentation**: All key docs in docs/ref/ with comprehensive PRD and concepts