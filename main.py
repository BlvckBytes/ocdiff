import plistlib
import pprint

# TODO: Add CLI parameters for a, b, ignore-disabled
# TODO: Add proper ASCII representation

''' Get a value from a plist-dict by it's dot separated path'''
def getVal(pl, path):
  # Try to access the full path level by level
  keys = path.split('.')
  curr = pl
  try:
    for key in keys:
      curr = curr[key]
  # Return None if the key doesn't exist on b
  except KeyError:
    return None
  return curr

''' Make diff result list entry '''
def mkEntry(a, b, path, isrev, res):
  # Create empty array
  if not path in res:
    res[path] = []

  targ = res[path]

  # Generate new entry
  entry = { 'a': a, 'b': b } if not isrev else { 'a': b, 'b': a }

  # Don't append duplicates
  for i in targ:
    if i == entry:
      return

  targ.append(entry)

''' Check whether or not two dicts equal (scalar values only) '''
def dictEq(a, b):
  for key in a:
    if a.get(key) != b.get(key):
      return False
  return True

''' Diff two plists by checking them against each other '''
def diffPlists(a, b):
  res = {}
  # Diff a against b
  for key in a.keys():
    diffKey(a, b, key, key, False, res)
  # Diff b against a
  for key in a.keys():
    diffKey(b, a, key, key, True, res)
  return res

''' Diff only known and unique-ifying keys, return a score of matched values '''
def diffKnownKeys(a, b):
  knownKeys = [
    'BundlePath', 'ExecutablePath', 'Path', 'Address', 'Find', 'Replace', 'Identifier'
  ]

  score = 0
  for key in knownKeys:
    # Key not in both dicts
    if key not in a or key not in b:
      continue

    # Increase score on matching keys
    if a.get(key) == b.get(key):
      score = score + 1

  return score

''' Find most similar matching dict within list by known keys '''
def findMostSimilar(a, lst):
  # Generate hit-list
  hits = [[b, diffKnownKeys(a, b)] for b in lst]
  hits = list(filter(lambda x: x[1] != 0, hits))

  # No similar items
  if len(hits) == 0:
    return None

  # Return most similar
  hits.sort(key=lambda x: x[1], reverse=True)
  return hits[0][0]

''' Diff a list by diffing it's items'''
def diffList(b, lst, path, isrev, res):
  pass
  other = getVal(b, path)
  # Not a list, comparison impossible
  if not isinstance(other, list):
    mkEntry(lst, '<not a list>', path, isrev, res)
    return

  for i in lst:
    if isinstance(i, list):
      raise NotImplementedError()

    isdict = isinstance(i, dict)
    exists = False
    for j in other:
      if isinstance(i, list):
        raise NotImplementedError()

      if isdict:
        # Can only compare dict again dict
        if not isinstance(j, dict):
          continue

        # Compare dicts
        if not dictEq(i, j):
          continue

        exists = True
        break

      # Compare scalars
      else:
        if i == j:
          exists = True
          break

    # Not existing exactly like this in the other list
    if not exists:
      if isdict:
        mkEntry(i, findMostSimilar(i, other), path, isrev, res)
      else:
        mkEntry(i, '<no list partner>', path, isrev, res)

''' Diff a scalar value (content and type is equal)'''
def diffScalar(b, v, path, isrev, res):
  other = getVal(b, path)
  if v != other:
    mkEntry(v, other, path, isrev, res)

''' Diff a key recursively (with all subkeys) '''
def diffKey(a, b, k, path, isrev, res):
  val = a[k]

  # Another key to a dict
  if isinstance(val, dict):
    for key in val:
      diffKey(val, b, key, f'{path}.{key}', isrev, res)
  else:
    # Diff list items
    if isinstance(val, list):
      diffList(b, val, path, isrev, res)
    # Diff scalar value
    else:
      diffScalar(b, val, path, isrev, res)

# Static for now, args later
fA='/Users/lenovo/Desktop/MacOS-XPS-9700-OpenCore/EFI/OC/config.plist'
fB='/Users/lenovo/Desktop/Misc/MacOS-XPS-9700-OpenCore/EFI/OC/config.plist'

# Open both files and invoke diffing
with open(fA, 'rb') as a:
  with open(fB, 'rb') as b:
    diffs = diffPlists(plistlib.load(a), plistlib.load(b))
    pprint.pprint(diffs)