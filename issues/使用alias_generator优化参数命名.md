# 使用alias_generator优化参数命名

## 背景
在前后端分离的项目中，经常遇到参数命名规范不统一的问题：
- **前端**：通常使用驼峰命名法（camelCase）
- **后端**：通常使用下划线命名法（snake_case）

## 之前的解决方案
手动为每个Query参数添加别名：

```python
# 不够优雅的方式
@app.get("/api/data")
async def get_data(
    use_cache: bool = Query(default=True, alias="useCache"),
    cache_ttl_minutes: int = Query(default=5, alias="cacheTtlMinutes")
):
    pass
```

**问题**：
- 需要手动为每个参数添加别名
- 容易遗漏，不够统一
- 维护成本高

## 优化后的解决方案
使用Pydantic的`alias_generator`和项目中的`@as_query`装饰器：

### 1. 创建查询参数模型
```python
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from module_admin.annotation.pydantic_annotation import as_query

@as_query
class ConnectivityStatsQueryModel(BaseModel):
    """连通性统计查询参数模型"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    use_cache: bool = Field(default=True, description="是否使用缓存")
    cache_ttl_minutes: int = Field(default=5, ge=1, le=60, description="缓存时间（分钟）")
```

### 2. 在控制器中使用
```python
@connectivityController.get('/statistics')
async def get_connectivity_statistics(
    request: Request,
    query_params: ConnectivityStatsQueryModel = Depends(ConnectivityStatsQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db)
):
    # 使用 query_params.use_cache 和 query_params.cache_ttl_minutes
    result = await ConnectivityService.get_connectivity_statistics(
        query_db, 
        use_cache=query_params.use_cache, 
        cache_ttl_minutes=query_params.cache_ttl_minutes
    )
```

## 优势分析

### 1. 自动命名转换
- `use_cache` → `useCache`
- `cache_ttl_minutes` → `cacheTtlMinutes`
- 无需手动维护别名映射

### 2. 统一性
- 与项目中其他模块保持一致
- 遵循既定的最佳实践

### 3. 类型安全
- 使用Pydantic模型提供完整的类型检查
- 支持字段验证（如范围限制：ge=1, le=60）

### 4. 文档友好
- FastAPI自动生成更完整的API文档
- 参数说明更清晰

### 5. 可维护性
- 查询参数定义集中在模型中
- 易于添加新参数和验证规则

## 实际应用
这个方案现在应用于：
- 连通性统计API：`/redfish/connectivity/statistics`
- 批量检测API：`/redfish/connectivity/batch-check`

## 配置说明
```python
model_config = ConfigDict(
    alias_generator=to_camel,        # 自动转换为驼峰命名
    populate_by_name=True           # 同时支持原始名称和别名
)
```

- `alias_generator=to_camel`：自动将snake_case转换为camelCase
- `populate_by_name=True`：既接受驼峰命名，也接受下划线命名（向后兼容）

## 推荐实践
1. **新API开发**：直接使用这种方式定义查询参数
2. **现有API优化**：逐步迁移到这种模式
3. **团队规范**：建议所有复杂查询参数都使用这种方式

## 注意事项
- `@as_query`装饰器是项目特有的，确保正确导入
- `populate_by_name=True`保证向后兼容性
- 对于简单的单个参数，直接使用Query()仍然是合理的选择

这种方式大大提高了代码的可维护性和一致性，建议在项目中广泛采用。 