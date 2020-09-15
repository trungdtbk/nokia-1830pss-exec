# PSS1830-Executor

PSS-1830-Exec allows to run any command as CLI or as root in Nokia 1830-PSS Network Elements.

# Installation

## Install from source
  ```
  # git clone https://github.com/trungdtbk/nokia-1830pss-exec.git`
  # cd nokia-1830pss-exec
  # python setup.py install
  # pssexec -v
  ```

# Usage Examples

## Gather General Information
`pssexec -m cli -u admin -p admin -c "show gen det" "show soft up sta"`

## Gather Memory Info
`pssexec -m root -u root -p root -c "vmstat -s | head -n 5"`