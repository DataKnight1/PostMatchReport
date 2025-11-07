from ETL.loaders.data_loader import DataLoader
from ETL.transformers.match_processor import MatchProcessor

loader = DataLoader('./cache')
ws,fm = loader.load_all_data(1946652,4947905,True)
proc = MatchProcessor(ws,fm)
shots = proc.get_shots(None)
print('shots shape', shots.shape)
print('columns', list(shots.columns)[:50])
subset = shots[['teamId','playerId','type_display','outcome_display','is_goal','is_own_goal','x','y','xg','qualifiers_dict']].head(10)
for i,row in subset.iterrows():
    print('row', i, row['type_display'], row['outcome_display'], 'goal?', row['is_goal'], 'own?', row['is_own_goal'],'xg', row['xg'])
    q = row['qualifiers_dict']
    if isinstance(q, dict):
        keys = list(q.keys())
        print('  q keys:', keys[:20])
