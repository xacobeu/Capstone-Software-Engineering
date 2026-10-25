"""Make a file-count CLT figure matching the existing input-size report figures."""
import argparse
import json
from pathlib import Path
import sys
from plot_clt_report import BASE, sha, plt, matplotlib


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=BASE/'analysis/report-figures')
    args=parser.parse_args()
    stem='clt-original-file-count'
    targets=[args.output/f'{stem}.{ext}' for ext in ['png','pdf','svg']]
    manifest_path=args.output/f'{stem}-manifest.json'
    checksums_path=args.output/f'{stem}-sha256.json'
    if any(p.exists() for p in [*targets,manifest_path,checksums_path]):
        parser.error('Choose a new output directory; existing artifacts are preserved.')
    source=BASE/'results/integrated-full/summary.json'
    source_hash=sha(source)
    summary={r['scenario']:r for r in json.loads(source.read_text())}
    counts=[1,4,16,32]
    rows=[summary[f'count-{n}'] for n in counts]
    for row,count,reference in zip(rows,counts,[11.754,12.025,14.721,19.892]):
        assert row['count']==count and row['bytes']==65536 and row['failures']==0
        assert row['contextMs']['n']==30 and round(row['contextMs']['median'],3)==reference
    median=[r['contextMs']['median'] for r in rows]
    p90=[r['contextMs']['p90'] for r in rows]
    low=[r['contextMs']['medianCI95'][0] for r in rows]
    high=[r['contextMs']['medianCI95'][1] for r in rows]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,
        'axes.labelsize':11.5,'xtick.labelsize':11,'ytick.labelsize':11,
        'legend.fontsize':10,'figure.facecolor':'white','axes.facecolor':'white',
        'svg.fonttype':'none','pdf.fonttype':42,'savefig.facecolor':'white'})
    fig,ax=plt.subplots(figsize=(9,5.5),layout='constrained')
    med=ax.errorbar(counts,median,yerr=[[m-l for m,l in zip(median,low)],
        [h-m for m,h in zip(median,high)]],fmt='o-',color='#1764ab',linewidth=1.8,
        markersize=6,capsize=4,elinewidth=1.5,zorder=3)
    tail,=ax.plot(counts,p90,'s--',color='#d06a00',linewidth=1.8,markersize=6,zorder=2)
    ax.set_title('Context Loading Time vs. Number of Files — Original Experiment',pad=14)
    ax.set_xlabel('Number of Context Files',labelpad=9)
    ax.set_ylabel('Context Loading Time (ms)',labelpad=9)
    ax.set_xticks(counts);ax.minorticks_off();ax.set_ylim(9,35);ax.set_yticks([10,15,20,25,30,35])
    ax.grid(True,color='#b8c0c8',alpha=.28,linewidth=.7)
    ax.spines[['top','right']].set_visible(False)
    ax.legend([med,tail],['Median (95% Bootstrap CI)','90th Percentile (P90)'],
        loc='upper left',frameon=True,framealpha=1,facecolor='white',edgecolor='#cccccc')
    assert list(med.lines[0].get_ydata())==median and list(tail.get_ydata())==p90
    for i,segment in enumerate(med.lines[2][0].get_segments()):
        assert list(segment[:,1])==[low[i],high[i]]
    assert not ax.texts and not fig.texts
    fig.canvas.draw()
    for text in [ax.title,ax.xaxis.label,ax.yaxis.label,*ax.get_xticklabels(),*ax.get_yticklabels()]:
        box=text.get_window_extent();bounds=fig.bbox
        assert box.x0>=bounds.x0-1 and box.y0>=bounds.y0-1 and box.x1<=bounds.x1+1 and box.y1<=bounds.y1+1
    args.output.mkdir(parents=True,exist_ok=True)
    for target in targets:fig.savefig(target,dpi=300)
    plt.close(fig)
    assert sha(source)==source_hash
    manifest={'source':str(source.relative_to(BASE)),'source_sha256':source_hash,
        'script_sha256':sha(Path(__file__)),'style_reference_sha256':sha(Path(__file__).with_name('plot_clt_report.py')),
        'python':sys.version,'matplotlib':matplotlib.__version__,'invocation':sys.argv,
        'png_dpi':300,'fixed_total_input_bytes':65536,'x_scale':'linear',
        'statistics':'Recorded summary medians, P90 and bootstrap median CI reused without recalculation.',
        'plotted_values':[{'count':c,'median':m,'p90':p,'medianCI95':[l,h]} for c,m,p,l,h in zip(counts,median,p90,low,high)]}
    manifest_path.write_text(json.dumps(manifest,indent=2))
    checksums_path.write_text(json.dumps({p.name:sha(p) for p in [*targets,manifest_path]},indent=2))
    print('Generated and validated:',*[str(p) for p in targets],sep='\n')

if __name__=='__main__':main()
