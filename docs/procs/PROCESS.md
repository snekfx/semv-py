# SEMV Python - Master Workflow Guide

## PROJECT STRUCTURE & KEY DOCUMENTS

### Process Documents (docs/procs/)
- **PROCESS.md** ← You are here - Master workflow guide
- **CONTINUE.md** ← Session handoff status (CRITICAL: update every session)
- **QUICK_REF.md** ← 30-second essential context
- **SPRINT.md** ← Current active tasks and priorities
- **ROADMAP.md** ← Strategic milestones and phases
- **TASKS.md** ← Detailed task breakdown with story points
- **DONE.md** ← Completed work archive

### Reference Documents (docs/ref/)
- **semv_concepts.md** ← Core SEMV architecture and patterns
- **plan/semv_prd.md** ← Product Requirements Document
- **plan/semv_python_buildout_plan.md** ← Implementation strategy
- **plan/semv_roadmap.md** ← Original project roadmap
- **integration/** ← Boxy, GitSim, Blade integration guides
- **detection/** ← Project detection strategies
- **pypi_publishing_guide.md** ← Publishing instructions

### Analysis Results (.analysis/)
- **consolidated_wisdom.txt** ← China's project analysis and insights

## SELF-HYDRATING WORKFLOW PROCESS

### Step 1: Context Hydration Checklist
When starting any session, always follow this sequence:
1. **Read CONTINUE.md** ← Understand current session context and blocks
2. **Check SPRINT.md** ← Identify active tasks and priorities
3. **Review QUICK_REF.md** ← Refresh critical project context
4. **Validate with ./bin/validate-docs.sh** ← Ensure documentation integrity

### Step 2: Phase Detection
Current project is in **Development Phase - Python Rewrite**
- **Focus**: Converting 4,000-line Bash script to modular Python
- **Architecture**: Core modules, parsers, adapters, integration layers
- **Target**: 800-1,200 lines, 70% reduction, 10x performance

### Step 3: Work Execution Patterns

#### Development Session Pattern:
1. Review current branch status and active PRs
2. Select task from SPRINT.md by priority
3. Implement following existing patterns in docs/ref/semv_concepts.md
4. Test thoroughly with modular architecture
5. Update documentation as needed
6. **MANDATORY**: Update CONTINUE.md with session progress

#### Planning Session Pattern:
1. Review ROADMAP.md for strategic alignment
2. Break down epics in TASKS.md into implementable stories
3. Update SPRINT.md with prioritized tasks
4. Adjust timelines based on complexity analysis

### Step 4: Session Closure & Handoff Requirements

**MANDATORY CONTINUE.md Update Format:**
```markdown
## HANDOFF-[YYYY-MM-DD]-[HHMM]
### Session Duration: [X hours]
### Branch: [current branch]
### Completed:
- [Specific items with file references]
### Blocked:
- [Any blockers with context]
### Next Agent MUST:
- [Critical immediate actions]
### Context Hash: [git commit SHA]
### Files Modified: [count]
```

## PROJECT STATUS QUICK REFERENCE

### Current Priorities
1. **Architecture Design** - Modular Python structure (HIGH)
2. **Core Module Development** - Version parsing, git ops (HIGH)
3. **Integration Layer** - Boxy, GitSim adapters (MEDIUM)
4. **Testing & Validation** - Comprehensive test suite (HIGH)

### Progress Tracking
- **Phase**: Early development/architecture
- **Completion**: Architecture ~30%, Implementation ~10%
- **Next Milestone**: Core module MVP

### Key Decisions & Context
- **Language Support**: Rust, JavaScript, Python, Bash (in scope)
- **Out of Scope**: Java, C/C++, Go support
- **Performance Target**: 10x improvement over Bash version
- **Integration**: Must work with Boxy workflow system

## COMMON WORKFLOWS

### Sprint Planning
1. Review ROADMAP.md strategic goals
2. Analyze TASKS.md for ready items
3. Prioritize by dependencies and complexity
4. Update SPRINT.md with committed tasks
5. Validate capacity against story points

### Development Session
```bash
# Start new session
git status                    # Check current state
./bin/validate-docs.sh       # Validate documentation
# Read CONTINUE.md -> SPRINT.md -> select task
# Implement following semv_concepts.md patterns
pytest                       # Run tests (when available)
# Update CONTINUE.md before session end
```

### Milestone Transition
1. Archive completed sprint to DONE.md
2. Update ROADMAP.md with progress
3. Generate next SPRINT.md from TASKS.md
4. Validate all documentation integrity

## AGENT QUICK START GUIDE

### Essential Project Background
**SEMV** (Semantic Version Manager) automates version management across multi-language projects using intelligent synchronization and semantic version analysis.

### Key Architecture Principles
- **Single Responsibility**: Each module handles one concern
- **Dependency Injection**: Configurable, testable components
- **Graceful Degradation**: Fallbacks for missing tools/features
- **Configuration-Driven**: Behavior controlled through config files

### Development Patterns
- **Modular Design**: Core + parsers + adapters + integrations
- **Error Handling**: Comprehensive error states with recovery
- **Testing**: Unit tests for all core functionality
- **Documentation**: Inline docstrings + architectural docs

### Workflow Rules & Conventions
1. **Always** update CONTINUE.md at session end
2. **Never** commit without running tests (when available)
3. **Follow** existing patterns in semv_concepts.md
4. **Maintain** backward compatibility with Bash SEMV
5. **Document** all architectural decisions

## REFERENCE LINKS

### Essential Files by Priority
1. **docs/ref/semv_concepts.md** - Core patterns and philosophy
2. **docs/ref/plan/semv_prd.md** - Product requirements
3. **docs/procs/CONTINUE.md** - Current session status
4. **docs/procs/SPRINT.md** - Active tasks
5. **docs/ref/plan/semv_python_buildout_plan.md** - Implementation strategy

### Topic-Specific References
- **Architecture**: docs/ref/semv_concepts.md
- **Integration**: docs/ref/integration/
- **Detection**: docs/ref/detection/
- **Publishing**: docs/ref/pypi_publishing_guide.md

### Testing & Validation Tools
- **./bin/validate-docs.sh** - Documentation validation
- **pytest** - Python testing framework (when configured)
- **semv -help** - Reference Bash implementation

## CRITICAL SUCCESS FACTORS

1. **Update CONTINUE.md every session** - Maintains handoff quality
2. **Follow modular architecture** - Enables 70% size reduction goal
3. **Test thoroughly** - Ensures reliability and performance
4. **Document decisions** - Preserves architectural knowledge
5. **Validate regularly** - Prevents documentation debt

---

================================================================================
Important! Agentic Non-Detemrinstic Safety Rules (NDSR)
================================================================================
For any test run or command that may
- be too long running
- be interactive, pty or tty bound
- be network, socket, process or event bound
- be a running service/process/daemon
- be non-deterministic in nature
- require elevated permissions or authentication (sudo etc)
You MUST use timeouts and/or redirection at a bare minimum! (Redirect output to a temp file to read the result. after timeout ellapse)
You MUST sanity check base assumptions and resource availability in a robust manner!
can use a shell script to wrap the invocation with safeguards!
can ask the user to run the commands (provide precise command to run and make it copy-pastable)

You must NOT let commands that can run indefinitely run in your agentic context because you are not time bound
and cannot see how long things take. You must use a reasonable timeout for the type of work expected, and if
the work results in a timeout failure you can determine why the work did not execute in the alloted time,
or else slightly modify the timeout tolerance. You will not be able to determine if a system or command is hanging our running infinitely without proper safeguards.


Potential Hanging Danger Signs:
- large file processes (reading files larger than 5mb) 
  .. start tests that prove a baseline with smaller file sizes
- http servers, daemon process, REPL 
  .. wrap with a shell level timeout, or use a direct invocation version that is not a REPL or Daemon
- event-driven designs, network, parallel processes, streaming, async
  .. wrap with a shell level timeout, and sanity test blocking calls first
  .. use tools like ping curl nestat, etc with timeout bounds
- long running build processes, installations, or upgrades
  .. if they fail timeouts, ask the user to try to run them for you
- user complains about timing of tasks or evidence of jobs taking longer than normal
  .. timebound tasks or ask the user to try
- command failures or general resource failures
  .. disk space, memory, network or other system level issues. 
- require sudo or authentication
  .. user should run sudo commands, auth tokens expired or wrong path

General Sanity/Assumption Pre-Check
If there is potential for hanging danger, different levels of review:
- make sure blocking calls used by non-detemrinistic apis pass a baseline sanity check 
- make sure necessary system resources, tools, paths, urls etc are available through robust means
- make sure potentially incomplete or corrupted code did not result in an unreachable condition
- make sure previous refactors did not result in code or workflow corruption
- do not assume code is correct and exists without proof of green tests and sanity tests
- do not assume tests are correct without verifying validity of tests
- do not run commands that require sudo or interactive shell prompts that dont accept pipe input


**Last Updated**: Session initialization
**Next Review**: After first development milestone
