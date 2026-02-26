import pytest
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_get_graph_with_checkpointer():
    """Test that the graph is compiled with an AsyncPostgresSaver checkpointer."""
    from app.agents.graph import get_graph_with_checkpointer

    # Mock settings
    with patch("app.agents.graph.settings") as mock_settings:
        mock_settings.database_url = "postgresql://postgres:postgres@localhost:5432/postgres"

        # Mock app.agents.graph.get_pool
        with patch("app.agents.graph.get_pool") as mock_get_pool, \
             patch("app.agents.graph.AsyncPostgresSaver") as mock_saver_class:

            mock_pool = MagicMock()
            mock_conn = AsyncMock()
            mock_pool.connection.return_value.__aenter__.return_value = mock_conn
            mock_get_pool.return_value = mock_pool

            mock_saver = MagicMock()
            mock_saver.setup = AsyncMock()
            mock_saver_class.return_value = mock_saver

            # Mock build_graph and its compile method
            with patch("app.agents.graph.build_graph") as mock_build_graph:
                mock_builder = MagicMock()
                mock_graph = MagicMock()
                mock_builder.compile.return_value = mock_graph
                mock_build_graph.return_value = mock_builder

                async with get_graph_with_checkpointer() as graph:
                    assert graph == mock_graph

                # Verify setup was called
                mock_saver.setup.assert_called_once()
                mock_builder.compile.assert_called_once_with(checkpointer=mock_saver)
