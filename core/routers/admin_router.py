from fastapi import APIRouter, Depends

from core.tasks.table import TableSync

router = APIRouter(prefix='/admin')


@router.post('/sync_table', response_model=dict)
async def sync_table_db(table: TableSync = Depends()) -> dict:
    await table.sync_table()
    return {'status': 'success'}
