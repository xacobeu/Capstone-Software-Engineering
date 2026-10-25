"""Render two consistent CLT report figures using recorded statistics only."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parents[2]
EXPERIMENTS = [
    ('original', BASE/'results/integrated-full/summary.json',
     ['bytes-4096','bytes-16384','bytes-65536','bytes-262144'],
     [4096,16384,65536,262144], ['4 KiB','16 KiB','64 KiB','256 KiB'],
     [12.244,11.841,12.324,12.294], (9,19)),
    ('extension', BASE/'results/context-size-extension-v2/full-2026-10-14T00-15-51.571Z-gKVrD3/summary.json',
     ['size-ext-00065536','size-ext-00262144','size-ext-01048576','size-ext-04194304','size-ext-16777216'],
     [65536,262144,1048576,4194304,16777216], ['64 KiB','256 KiB','1 MiB','4 MiB','16 MiB'],
     [11.246,11.472,12.079,14.752,24.107], (9,35)),
]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=BASE/'analysis/report-figures')
    args=parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):parser.error('Choose a new output directory; existing figures are preserved.')
    source_hashes={str(e[1].relative_to(BASE)):sha(e[1]) for e in EXPERIMENTS}
    selected={}
    for name,source,ids,sizes,ticks,reference,limits in EXPERIMENTS:
        all_rows=json.loads(source.read_text())
        by_id={r['scenario']:r for r in all_rows}
        rows=[by_id[i] for i in ids]
        assert len(by_id)==len(all_rows), 'Duplicate scenario'
        for r,size,expected in zip(rows,sizes,reference):
            v=r['contextMs']
            assert r['count']==4 and r['bytes']==size and r['failures']==0 and v['n']==30
            assert round(v['median'],3)==expected
            assert all(math.isfinite(x) for x in [v['median'],v['p90'],*v['medianCI95']])
            assert v['medianCI95'][0]<=v['median']<=v['medianCI95'][1]
        selected[name]=rows
    args.output.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,
        'axes.labelsize':11.5,'xtick.labelsize':11,'ytick.labelsize':11,
        'legend.fontsize':10,'figure.facecolor':'white','axes.facecolor':'white',
        'svg.fonttype':'none','pdf.fonttype':42,'savefig.facecolor':'white'})
    verified={}
    for name,source,ids,sizes,ticks,reference,limits in EXPERIMENTS:
        rows=selected[name]
        median=[r['contextMs']['median'] for r in rows]
        p90=[r['contextMs']['p90'] for r in rows]
        low=[r['contextMs']['medianCI95'][0] for r in rows]
        high=[r['contextMs']['medianCI95'][1] for r in rows]
        fig,ax=plt.subplots(figsize=(9,5.5),layout='constrained')
        med_artist=ax.errorbar(sizes,median,yerr=[[m-l for m,l in zip(median,low)],
            [h-m for m,h in zip(median,high)]],fmt='o-',color='#1764ab',
            linewidth=1.8,markersize=6,capsize=4,elinewidth=1.5,zorder=3)
        p90_artist,=ax.plot(sizes,p90,'s--',color='#d06a00',linewidth=1.8,markersize=6,zorder=2)
        title=f'Context Loading Time vs. Input Size — {name.title()} Experiment'
        ax.set_title(title,pad=14)
        ax.set_xlabel('Total Context Input Size (log scale)',labelpad=9)
        ax.set_ylabel('Context Loading Time (ms)',labelpad=9)
        ax.set_xscale('log',base=2);ax.set_xticks(sizes,ticks);ax.minorticks_off()
        ax.set_ylim(*limits)
        ax.set_yticks([10,12,14,16,18] if name=="original" else [10,15,20,25,30,35])
        ax.grid(True,color='#b8c0c8',alpha=.28,linewidth=.7)
        ax.spines[['top','right']].set_visible(False)
        legend=ax.legend([med_artist,p90_artist],['Median (95% Bootstrap CI)',
            '90th Percentile (P90)'],loc='upper left',frameon=True,framealpha=1,
            facecolor='white',edgecolor='#cccccc')
        # Validate the actual artists, not a transcription from the screenshot.
        assert list(med_artist.lines[0].get_ydata())==median
        assert list(p90_artist.get_ydata())==p90
        for i,segment in enumerate(med_artist.lines[2][0].get_segments()):
            assert list(segment[:,1])==[low[i],high[i]]
        assert len(ax.texts)==0 and len(fig.texts)==0
        assert [t.get_text() for t in legend.get_texts()]==['Median (95% Bootstrap CI)','90th Percentile (P90)']
        fig.canvas.draw()
        bbox=fig.bbox
        for text in [ax.title,ax.xaxis.label,ax.yaxis.label,*ax.get_xticklabels(),*ax.get_yticklabels()]:
            box=text.get_window_extent()
            assert box.x0>=bbox.x0-1 and box.y0>=bbox.y0-1 and box.x1<=bbox.x1+1 and box.y1<=bbox.y1+1, 'Clipped label'
        stem=f'clt-{name}-input-size'
        for ext in ['png','pdf','svg']:
            fig.savefig(args.output/f'{stem}.{ext}',dpi=300)
        plt.close(fig)
        verified[name]=[{'scenario':r['scenario'],'bytes':r['bytes'],'median':m,
            'p90':p,'medianCI95':[l,h]} for r,m,p,l,h in zip(rows,median,p90,low,high)]
    assert source_hashes=={str(e[1].relative_to(BASE)):sha(e[1]) for e in EXPERIMENTS}
    manifest={'source_sha256':source_hashes,'script_sha256':sha(Path(__file__)),
        'python':sys.version,'matplotlib':matplotlib.__version__,'invocation':sys.argv,
        'png_dpi':300,'size_inches':[9,5.5],'statistics':'Authoritative summaries reused exactly; no statistics estimated or recalculated; sessions kept separate.',
        'artist_validation':'median, p90 and CI endpoints match recorded summaries; exact labels; no extra figure text; no clipped labels',
        'plotted_values':verified}
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2))
    (args.output/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in args.output.iterdir() if p.is_file()},indent=2))
    print(f'Generated and validated six exports: {args.output}')

if __name__=='__main__':main()
