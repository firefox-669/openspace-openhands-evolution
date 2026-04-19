"""
OpenSpace-OpenHands-Evolution 命令行入口

提供类似 openspace 命令的 CLI 体验
"""

import asyncio
import argparse
import sys
from typing import Optional

from .orchestrator import EvolutionOrchestrator, TaskRequest
from .config_loader import load_config


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀 OpenSpace-OpenHands-Evolution                        ║
║      Self-Evolving AI Programming Assistant               ║
║                                                           ║
║   Make Your AI Programmer:                                ║
║   • Smarter (自我进化)                                     ║
║   • Low-Cost (成本优化)                                   ║
║   • Cross-Project (跨项目复用)                             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """打印帮助信息"""
    help_text = """
📖 可用命令:

  interactive     交互模式（默认）
  run <query>     执行单个任务
  transfer        跨项目技能迁移
  status          查看系统状态
  help            显示此帮助信息
  exit/quit/q     退出程序

💡 示例:

  # 交互模式
  openspace-evolution

  # 执行单个任务
  openspace-evolution run "创建 Flask API"

  # 跨项目迁移
  openspace-evolution transfer --from project-a --to project-b

  # 查看状态
  openspace-evolution status

⚙️  选项:

  --config, -c    配置文件路径
  --model, -m     LLM 模型名称
  --project       项目 ID
  --no-ui         禁用 UI（纯文本模式）
  --verbose       详细输出模式
    """
    print(help_text)


async def interactive_mode(orchestrator: EvolutionOrchestrator, project_id: str):
    """交互模式"""
    print("\n" + "="*60)
    print("  🎯 交互模式 - 输入任务描述开始")
    print("="*60)
    print("  输入 'help' 查看帮助，'exit' 退出\n")
    
    while True:
        try:
            query = input(">>> ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 再见！")
                break
            
            if query.lower() == 'help':
                print_help()
                continue
            
            if query.lower() == 'status':
                await show_status(orchestrator)
                continue
            
            # 执行任务
            print(f"\n🚀 执行任务: {query}\n")
            
            task = TaskRequest(
                id=f"task-{id(query)}",
                description=query,
                project_id=project_id,
                language="python"
            )
            
            result = await orchestrator.execute_task(task)
            
            if result.success:
                print(f"\n✅ 任务成功!")
                print(f"   输出: {result.output[:200]}")
                if result.metrics:
                    score = result.metrics.get('overall_score', 0)
                    print(f"   质量评分: {score:.2f}")
                if result.evolved_skills:
                    print(f"   进化技能: {', '.join(result.evolved_skills)}")
            else:
                print(f"\n❌ 任务失败: {result.error}")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}\n")


async def single_query_mode(orchestrator: EvolutionOrchestrator, query: str, project_id: str):
    """单查询模式"""
    print(f"\n🚀 执行任务: {query}\n")
    
    task = TaskRequest(
        id="single-query",
        description=query,
        project_id=project_id,
        language="python"
    )
    
    result = await orchestrator.execute_task(task)
    
    if result.success:
        print(f"\n✅ 任务成功!")
        print(f"\n输出:\n{result.output}")
        if result.metrics:
            score = result.metrics.get('overall_score', 0)
            print(f"\n质量评分: {score:.2f}")
        if result.evolved_skills:
            print(f"\n进化的技能: {', '.join(result.evolved_skills)}")
    else:
        print(f"\n❌ 任务失败: {result.error}")
        sys.exit(1)


async def show_status(orchestrator: EvolutionOrchestrator):
    """显示系统状态"""
    print("\n" + "="*60)
    print("  📊 系统状态")
    print("="*60)
    
    try:
        status = await orchestrator.get_system_status()
        
        print(f"\n  OpenSpace Engine: {status['openspace']['status']}")
        print(f"  OpenHands Engine: {status['openhands']['status']}")
        print(f"  Monitor System:   {status['monitor']['status']}")
        print(f"  Governance Layer: {status['governance']['status']}")
        print(f"\n  时间戳: {status['timestamp']}")
        
    except Exception as e:
        print(f"\n  ❌ 获取状态失败: {e}")
    
    print()


def create_parser() -> argparse.ArgumentParser:
    """创建参数解析器"""
    parser = argparse.ArgumentParser(
        description='OpenSpace-OpenHands-Evolution - 自进化 AI 编程助手',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                              # 交互模式
  %(prog)s run "创建 Flask API"         # 执行单个任务
  %(prog)s status                       # 查看状态
  %(prog)s --help                       # 显示帮助
        """
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # run 子命令
    run_parser = subparsers.add_parser('run', help='执行单个任务')
    run_parser.add_argument('query', type=str, help='任务描述')
    
    # transfer 子命令
    transfer_parser = subparsers.add_parser('transfer', help='跨项目技能迁移')
    transfer_parser.add_argument('--from', dest='source', type=str, required=True, help='源项目')
    transfer_parser.add_argument('--to', dest='target', type=str, required=True, help='目标项目')
    transfer_parser.add_argument('--similarity', type=float, default=0.7, help='最小相似度')
    
    # status 子命令
    subparsers.add_parser('status', help='查看系统状态')
    
    # 通用参数
    parser.add_argument('--config', '-c', type=str, help='配置文件路径')
    parser.add_argument('--model', '-m', type=str, help='LLM 模型名称')
    parser.add_argument('--project', '-p', type=str, default='default', help='项目 ID')
    parser.add_argument('--no-ui', action='store_true', help='禁用 UI')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    return parser


async def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 打印横幅
    if not args.no_ui:
        print_banner()
    
    # 加载配置
    try:
        config = load_config(args.config)
        
        # 应用命令行覆盖
        if args.model:
            config['openhands']['model'] = args.model
        
        if args.verbose:
            config['system']['log_level'] = 'DEBUG'
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        print("使用默认配置...")
        config = {
            'openspace': {'registry_path': './data/skills'},
            'openhands': {'model': args.model or 'gpt-4'},
            'monitor': {'quality_threshold': 0.8},
            'governance': {'enable_gatekeeping': True}
        }
    
    # 初始化编排器
    try:
        print("⚙️  初始化系统...")
        orchestrator = EvolutionOrchestrator(config)
        print("✅ 系统就绪\n")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)
    
    # 执行命令
    try:
        if args.command == 'run':
            # 单查询模式
            await single_query_mode(orchestrator, args.query, args.project)
        
        elif args.command == 'transfer':
            # 跨项目迁移
            from .orchestrator import TransferRequest
            
            print(f"🔄 跨项目迁移: {args.source} → {args.target}\n")
            
            transfer_request = TransferRequest(
                source_project=args.source,
                target_project=args.target,
                min_similarity=args.similarity
            )
            
            result = await orchestrator.cross_project_transfer(transfer_request)
            
            print(f"✅ 迁移完成!")
            print(f"   迁移技能数: {result.transferred_count}")
            print(f"   风险等级: {result.risk_assessment.get('risk_level', 'unknown')}")
        
        elif args.command == 'status':
            # 显示状态
            await show_status(orchestrator)
        
        else:
            # 交互模式（默认）
            await interactive_mode(orchestrator, args.project)
    
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_main():
    """运行主函数（入口点）"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
        sys.exit(0)


if __name__ == "__main__":
    run_main()
